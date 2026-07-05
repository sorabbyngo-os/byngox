use std::collections::HashMap;

use crate::AIModel;

pub struct ModelRegistry {
    models: HashMap<String, AIModel>,
}

impl ModelRegistry {
    pub fn new() -> Self {
        Self {
            models: HashMap::new(),
        }
    }

    pub fn register(&mut self, model: AIModel) {
        self.models.insert(model.id.clone(), model);
    }

    pub fn unregister(&mut self, id: &str) {
        self.models.remove(id);
    }

    pub fn get(&self, id: &str) -> Option<&AIModel> {
        self.models.get(id)
    }

    pub fn all(&self) -> Vec<&AIModel> {
        self.models.values().collect()
    }
}
