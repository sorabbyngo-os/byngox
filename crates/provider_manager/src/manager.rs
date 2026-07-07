use crate::{ProviderRegistry, ProviderType};

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

    pub fn provider(&self, provider_name: &str) -> Option<&ProviderType> {
        self.registry.get(provider_name)
    }
}
