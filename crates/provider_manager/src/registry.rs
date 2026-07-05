use std::collections::HashMap;

use crate::InferenceProvider;

pub struct ProviderRegistry {

    providers:

        HashMap<String, Box<dyn InferenceProvider>>,

}

impl ProviderRegistry {

    pub fn new() -> Self {

        Self {

            providers: HashMap::new(),

        }

    }

    pub fn register(

        &mut self,

        provider: Box<dyn InferenceProvider>,

    ) {

        self.providers

            .insert(provider.id().into(), provider);

    }

    pub fn get(

        &self,

        id:&str,

    ) -> Option<&Box<dyn InferenceProvider>> {

        self.providers.get(id)

    }

}
