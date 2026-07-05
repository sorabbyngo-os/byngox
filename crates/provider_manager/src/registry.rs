use std::collections::HashMap;

use crate::ModelProvider;

pub struct ProviderRegistry {

    providers: HashMap<String, Box<dyn ModelProvider>>,
}

impl ProviderRegistry {

    pub fn new() -> Self {

        Self {

            providers: HashMap::new(),
        }

    }

    pub fn register(

        &mut self,

        provider: Box<dyn ModelProvider>,

    ) {

        let id = provider.info().id.clone();

        self.providers.insert(id, provider);

    }

    pub fn get(

        &self,

        id:&str,

    ) -> Option<&Box<dyn ModelProvider>> {

        self.providers.get(id)

    }

}
