use crate::registry::ProviderRegistry;

pub struct ProviderManager {

    registry: ProviderRegistry,

}

impl ProviderManager {

    pub fn new() -> Self {

        Self {

            registry: ProviderRegistry::new(),

        }

    }

    pub fn registry(

        &mut self,

    ) -> &mut ProviderRegistry {

        &mut self.registry

    }

}
