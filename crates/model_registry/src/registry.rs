use std::collections::HashMap;

use ai_core::{Capability, Model};
pub struct ModelRegistry {
    models: HashMap<String, Model>,
}

impl ModelRegistry {
    pub fn new() -> Self {
        Self {
            models: HashMap::new(),
        }
    }

    pub fn register(&mut self, model: Model) {
        self.models.insert(model.id.clone(), model);
    }

    pub fn get(&self, id: &str) -> Option<&Model> {
        self.models.get(id)
    }

    pub fn models(&self) -> impl Iterator<Item = &Model> {
        self.models.values()
    }

    pub fn models_for(
        &self,
        capability: &Capability,
    ) -> Vec<Model> {
        self.models
            .values()
            .filter(|m| m.capabilities.contains(capability))
            .cloned()
            .collect()
    }
}
