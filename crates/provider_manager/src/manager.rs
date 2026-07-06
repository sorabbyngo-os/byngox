use crate::{
    ProviderRegistry,
    ProviderType,
};

use model_registry::Model;

pub struct ProviderManager {
    registry: ProviderRegistry,
}

impl ProviderManager {
    pub fn new() -> Self {
        Self {
            registry: ProviderRegistry::new(),
        }
    }

    pub fn registry_mut(&mut self) -> &mut ProviderRegistry {
        &mut self.registry
    }

    pub fn provider(
        &self,
        model: &Model,
    ) -> Option<&ProviderType> {
        self.registry.get(&model.provider)
    }
}
