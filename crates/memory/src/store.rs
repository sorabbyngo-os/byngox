use std::collections::HashMap;

#[derive(Default)]
pub struct MemoryStore {
    data: HashMap<String, Vec<String>>,
}

impl MemoryStore {
    pub fn new() -> Self {
        Self {
            data: HashMap::new(),
        }
    }

    pub fn store(&mut self, user: &str, memory: String) {
        self.data.entry(user.to_string()).or_default().push(memory);
    }

    pub fn retrieve(&self, user: &str) -> Vec<String> {
        self.data.get(user).cloned().unwrap_or_default()
    }
}
