use crate::{
    InferenceError,
    InferenceRequest,
    InferenceResponse,
};

use benchmark_engine::BenchmarkEngine;
use capability_registry::CapabilityRegistry;
use context::ContextManager;
use memory::MemoryManager;
use model_registry::ModelRegistry;
use model_router::ModelRouter;
use provider_manager::ProviderManager;
use resource_manager::ResourceManager;

pub struct InferenceEngine {

    capability_registry: CapabilityRegistry,

    model_registry: ModelRegistry,

    benchmark_engine: BenchmarkEngine,

    resource_manager: ResourceManager,

    router: ModelRouter,

    provider_manager: ProviderManager,

    memory: MemoryManager,

    context: ContextManager,
}

impl InferenceEngine {

    pub fn new() -> Self {

        Self {

            capability_registry: CapabilityRegistry::new(),

            model_registry: ModelRegistry::new(),

            benchmark_engine: BenchmarkEngine::new(),

            resource_manager: ResourceManager::new(),

            router: ModelRouter::new(),

            provider_manager: ProviderManager::new(),

            memory: MemoryManager::new(),

            context: ContextManager::new(),
        }
    }

    pub fn execute(

        &mut self,

        request: InferenceRequest,

    ) -> Result<InferenceResponse, InferenceError> {

        //--------------------------------------------------
        // STEP 1
        //--------------------------------------------------
     
       let capability = &request.capability;

        //--------------------------------------------------
        // STEP 2
        //--------------------------------------------------

        let candidates = self
            .model_registry
            .models_for(capability);

        //--------------------------------------------------
        // STEP 3
        //--------------------------------------------------

        let ranked =
            self.benchmark_engine.rank(candidates);

        //--------------------------------------------------
        // STEP 4
        //--------------------------------------------------

        let available =
            self.resource_manager.filter(ranked);

        //--------------------------------------------------
        // STEP 5
        //--------------------------------------------------

        let selected = self
           .router
           .select(available)
           .ok_or(InferenceError::NoModelAvailable)?;

        //--------------------------------------------------
        // STEP 6
        //------------------------------------------------
        let provider = self
            .provider_manager
            .provider(&selected.selection.provider)
            .ok_or(InferenceError::ProviderNotFound)?;

        //--------------------------------------------------
        // STEP 7
        //--------------------------------------------------

       let response = format!(
           "Provider {:?} executed: {}",
           provider,
           request.prompt
      );
  
      //--------------------------------------------------
        // STEP 8
        //--------------------------------------------------

        self.memory.store_interaction(

            &request.user_id,

            &request.prompt,

            &response,

        );

        Ok(

            InferenceResponse {

                model: selected.name().to_string(),

                output: response,
            }

        )

    }

}
