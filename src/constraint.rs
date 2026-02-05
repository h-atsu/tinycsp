use crate::domain::{Domain, Inconsistency};

#[derive(Clone, Debug)]
pub enum Constraint {
    NotEqual { x: usize, y: usize, offset: i32 },
    Equal { x: usize, value: i32 },
}

impl Constraint {
    pub fn propagate(&self, domains: &mut [Domain]) -> Result<bool, Inconsistency> {
        match *self {
            Constraint::NotEqual { x, y, offset } => {
                if domains[x].is_fixed() {
                    let v = domains[x].min().unwrap() as i32 - offset;
                    domains[y].remove(v)
                } else if domains[y].is_fixed() {
                    let v = domains[y].min().unwrap() as i32 + offset;
                    domains[x].remove(v)
                } else {
                    Ok(false)
                }
            }
            Constraint::Equal { x, value } => domains[x].fix(value),
        }
    }
}
