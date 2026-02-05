#[derive(Clone, Debug)]
pub struct Domain {
    n: usize,
    values: Vec<bool>,
    size: usize,
}

#[derive(Debug, Clone, Copy)]
pub struct Inconsistency;

impl Domain {
    pub fn from_values(n: usize, values: Vec<usize>) -> Result<Self, Inconsistency> {
        let mut flags = vec![false; n];
        let mut size = 0usize;
        for v in values {
            if v >= n {
                return Err(Inconsistency);
            }
            if !flags[v] {
                flags[v] = true;
                size += 1;
            }
        }
        if size == 0 {
            return Err(Inconsistency);
        }
        Ok(Self {
            n,
            values: flags,
            size,
        })
    }

    pub fn is_fixed(&self) -> bool {
        self.size == 1
    }

    pub fn min(&self) -> Option<usize> {
        self.values.iter().position(|&v| v)
    }

    pub fn remove(&mut self, value: i32) -> Result<bool, Inconsistency> {
        if value < 0 {
            return Ok(false);
        }
        let value = value as usize;
        if value >= self.n {
            return Ok(false);
        }
        if !self.values[value] {
            return Ok(false);
        }
        if self.size == 1 {
            return Err(Inconsistency);
        }
        self.values[value] = false;
        self.size -= 1;
        Ok(true)
    }

    pub fn fix(&mut self, value: i32) -> Result<bool, Inconsistency> {
        if value < 0 {
            return Err(Inconsistency);
        }
        let value = value as usize;
        if value >= self.n {
            return Err(Inconsistency);
        }
        if !self.values[value] {
            return Err(Inconsistency);
        }
        if self.size == 1 && self.values[value] {
            return Ok(false);
        }
        self.values.fill(false);
        self.values[value] = true;
        self.size = 1;
        Ok(true)
    }
}
