use std::collections::HashMap;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PySet;

mod constraint;
mod domain;
mod solver;

use constraint::Constraint;
use domain::{Domain, Inconsistency};
use solver::Solver;

#[pyfunction]
fn dfs_rs(
    py: Python<'_>,
    variables: Vec<Py<PyAny>>,
    constraints: Vec<Py<PyAny>>,
    on_solution: PyObject,
    stop_after_first: bool,
) -> PyResult<(bool, usize)> {
    let var_index = build_var_index(&variables);
    let domains = build_domains(py, &variables)?;
    let constraints = build_constraints(py, &constraints, &var_index)?;

    let mut solver = Solver::new(domains, constraints);
    let ok = solver.dfs(py, &on_solution, stop_after_first)?;
    Ok((ok, solver.n_recur()))
}

fn build_var_index(variables: &[Py<PyAny>]) -> HashMap<usize, usize> {
    let mut var_index = HashMap::with_capacity(variables.len());
    for (i, v) in variables.iter().enumerate() {
        var_index.insert(v.as_ptr() as usize, i);
    }
    var_index
}

fn build_domains(py: Python<'_>, variables: &[Py<PyAny>]) -> PyResult<Vec<Domain>> {
    let mut domains = Vec::with_capacity(variables.len());
    for var in variables {
        let dom = var.bind(py).getattr("dom")?;
        let n: usize = dom.getattr("n")?.extract()?;
        let values_any = dom.getattr("values")?;
        let values: Vec<usize> = if let Ok(set) = values_any.downcast::<PySet>() {
            let mut out = Vec::with_capacity(set.len());
            for item in set.iter() {
                out.push(item.extract::<usize>()?);
            }
            out
        } else {
            values_any.extract()?
        };
        let domain = Domain::from_values(n, values).map_err(|Inconsistency| {
            PyValueError::new_err("Inconsistent domain while building Rust solver")
        })?;
        domains.push(domain);
    }
    Ok(domains)
}

fn build_constraints(
    py: Python<'_>,
    constraints: &[Py<PyAny>],
    var_index: &HashMap<usize, usize>,
) -> PyResult<Vec<Constraint>> {
    let mut out = Vec::with_capacity(constraints.len());
    for c in constraints {
        let c_any = c.bind(py);
        if c_any.hasattr("y")? {
            let x_obj = c_any.getattr("x")?;
            let y_obj = c_any.getattr("y")?;
            let offset: i32 = c_any.getattr("offset")?.extract()?;
            let x = lookup_var_index(var_index, &x_obj)?;
            let y = lookup_var_index(var_index, &y_obj)?;
            out.push(Constraint::NotEqual { x, y, offset });
        } else if c_any.hasattr("value")? {
            let x_obj = c_any.getattr("x")?;
            let value: i32 = c_any.getattr("value")?.extract()?;
            let x = lookup_var_index(var_index, &x_obj)?;
            out.push(Constraint::Equal { x, value });
        } else {
            return Err(PyValueError::new_err(
                "Unknown constraint type while building Rust solver",
            ));
        }
    }
    Ok(out)
}

fn lookup_var_index(
    var_index: &HashMap<usize, usize>,
    var_obj: &Bound<'_, PyAny>,
) -> PyResult<usize> {
    let key = var_obj.as_ptr() as usize;
    var_index
        .get(&key)
        .copied()
        .ok_or_else(|| PyValueError::new_err("Constraint refers to unknown variable"))
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(dfs_rs, m)?)?;
    Ok(())
}
