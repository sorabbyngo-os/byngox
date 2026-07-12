use std::collections::HashMap;

use tool_capability::ToolCapability;

use crate::CapabilityProvider;

pub struct ProviderRegistry {
    providers: HashMap<ToolCapability, CapabilityProvider>,
}

impl ProviderRegistry {
    pub fn new() -> Self {
        Self {
            providers: HashMap::new(),
        }
    }

    pub fn register(&mut self, provider: CapabilityProvider) {
        self.providers.insert(provider.capability, provider);
    }

    pub fn resolve(&self, capability: ToolCapability) -> Option<&CapabilityProvider> {
        self.providers.get(&capability)
    }

    pub fn contains(&self, capability: ToolCapability) -> bool {
        self.providers.contains_key(&capability)
    }

    pub fn all(&self) -> impl Iterator<Item = &CapabilityProvider> {
        self.providers.values()
    }
}
