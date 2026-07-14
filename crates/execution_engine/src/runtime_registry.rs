use std::collections::HashMap;

use crate::Runtime;

pub struct RuntimeRegistry {
    runtimes: HashMap<String, Box<dyn Runtime>>,
}

impl RuntimeRegistry {
    pub fn new() -> Self {
        Self {
            runtimes: HashMap::new(),
        }
    }

    pub fn register(&mut self, runtime: Box<dyn Runtime>) {
        self.runtimes.insert(runtime.name().to_owned(), runtime);
    }

    pub fn runtime(&self, name: &str) -> Option<&dyn Runtime> {
        self.runtimes.get(name).map(Box::as_ref)
    }
}

impl Default for RuntimeRegistry {
    fn default() -> Self {
        Self::new()
    }
}
