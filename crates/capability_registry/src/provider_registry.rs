use std::collections::HashMap;

use ai_core::Capability;

use crate::CapabilityProvider;

pub struct ProviderRegistry {
    providers: HashMap<Capability, CapabilityProvider>,
}

impl ProviderRegistry {
    pub fn new() -> Self {
        Self {
            providers: HashMap::new(),
        }
    }

    pub fn register(&mut self, provider: CapabilityProvider) {
        self.providers.insert(provider.capability.clone(), provider);
    }

    pub fn resolve(&self, capability: Capability) -> Option<&CapabilityProvider> {
        self.providers.get(&capability)
    }

    pub fn contains(&self, capability: Capability) -> bool {
        self.providers.contains_key(&capability)
    }
}

impl Default for ProviderRegistry {
    fn default() -> Self {
        Self::new()
    }
}
