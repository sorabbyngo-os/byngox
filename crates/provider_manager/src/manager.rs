use crate::{
    InferenceRequest,
    InferenceResponse,
    ProviderRegistry,
};

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

    pub fn execute(

        &self,

        request: InferenceRequest,

    ) -> Option<InferenceResponse> {

        let provider = self.registry.get(&request.model)?;

        println!("Routing {:?} to {:?}", request.model, provider);

        Some(

            InferenceResponse {

                text: format!("Stub response for {}", request.prompt),

            }

        )

    }

}
