use std::collections::HashMap;

use crate::Capability;

pub struct CapabilityRegistry {

    capabilities: HashMap<String, Capability>,

}

impl CapabilityRegistry {

    pub fn new() -> Self {

        Self {

            capabilities: HashMap::new(),

        }

    }

    pub fn register(

        &mut self,

        capability: Capability,

    ) {

        self.capabilities.insert(

            capability.id.clone(),

            capability,

        );

    }

    pub fn get(

        &self,

        id:&str,

    ) -> Option<&Capability> {

        self.capabilities.get(id)

    }

    pub fn all(

        &self,

    ) -> impl Iterator<Item=&Capability> {

        self.capabilities.values()

    }
    
    pub fn resolve(
    &self,
    id: &str,
    ) -> Option<&Capability> {
    self.get(id)
    }
}
