use std::collections::HashMap;

use crate::ProviderType;

pub struct ProviderRegistry {
    providers: HashMap<String, ProviderType>,
}

impl ProviderRegistry {
    pub fn new() -> Self {
        Self {
            providers: HashMap::new(),
        }
    }

    pub fn register(&mut self, model: impl Into<String>, provider: ProviderType) {
        self.providers.insert(model.into(), provider);
    }

    pub fn get(&self, model: &str) -> Option<&ProviderType> {
        self.providers.get(model)
    }
}
