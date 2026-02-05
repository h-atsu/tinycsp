use pyo3::prelude::*;
use pyo3::types::{PyBool, PyTuple};

use crate::constraint::Constraint;
use crate::domain::{Domain, Inconsistency};

pub struct Solver {
    domains: Vec<Domain>,
    constraints: Vec<Constraint>,
    n_recur: usize,
}

impl Solver {
    pub fn new(domains: Vec<Domain>, constraints: Vec<Constraint>) -> Self {
        Self {
            domains,
            constraints,
            n_recur: 0,
        }
    }

    pub fn n_recur(&self) -> usize {
        self.n_recur
    }

    pub fn dfs(
        &mut self,
        py: Python<'_>,
        on_solution: &PyObject,
        stop_after_first: bool,
    ) -> PyResult<bool> {
        self.n_recur += 1;

        let not_fixed = self.first_not_fixed();

        if let Some(var_idx) = not_fixed {
            let val = self.domains[var_idx].min().unwrap() as i32;
            let backup = self.domains.clone();

            // left branch: x = val
            if self.domains[var_idx].fix(val).and_then(|_| self.fix_point()).is_ok() {
                if !self.dfs(py, on_solution, stop_after_first)? {
                    self.domains = backup;
                    return Ok(false);
                }
            }

            self.domains = backup.clone();

            // right branch: x != val
            if self.domains[var_idx]
                .remove(val)
                .and_then(|_| self.fix_point())
                .is_ok()
            {
                if !self.dfs(py, on_solution, stop_after_first)? {
                    self.domains = backup;
                    return Ok(false);
                }
            }

            Ok(true)
        } else {
            let solution = PyTuple::new_bound(
                py,
                self.domains
                    .iter()
                    .map(|d| d.min().unwrap() as i32),
            );
            let result = on_solution.call1(py, (solution,))?;

            if stop_after_first {
                return Ok(false);
            }

            let result_any = result.bind(py);
            if result_any.is_instance_of::<PyBool>() {
                let b: bool = result_any.extract()?;
                if !b {
                    return Ok(false);
                }
            }

            Ok(true)
        }
    }

    fn first_not_fixed(&self) -> Option<usize> {
        self.domains.iter().position(|d| !d.is_fixed())
    }

    fn fix_point(&mut self) -> Result<(), Inconsistency> {
        loop {
            let mut changed = false;
            for c in &self.constraints {
                changed |= c.propagate(&mut self.domains)?;
            }
            if !changed {
                return Ok(());
            }
        }
    }
}
