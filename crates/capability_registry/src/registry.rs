use std::collections::HashMap;

//use crate::{Capability, CapabilityDefinition, CapabilityProvider};
use crate::CapabilityDefinition;
pub struct CapabilityRegistry {
    //    providers: HashMap<Capability, Vec<CapabilityProvider>>,
    capabilities: HashMap<String, CapabilityDefinition>,
}

impl CapabilityRegistry {
    pub fn new() -> Self {
        Self {
            //          providers: HashMap::new(),
            capabilities: HashMap::new(),
        }
    }

    pub fn register(&mut self, capability: CapabilityDefinition) {
        self.capabilities.insert(capability.id.clone(), capability);
    }

    pub fn get(&self, id: &str) -> Option<&CapabilityDefinition> {
        self.capabilities.get(id)
    }

    pub fn all(&self) -> impl Iterator<Item = &CapabilityDefinition> {
        self.capabilities.values()
    }

    pub fn resolve(&self, id: &str) -> Option<&CapabilityDefinition> {
        self.get(id)
    }
}
