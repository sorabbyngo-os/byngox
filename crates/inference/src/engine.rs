use context::{
    Message,
    Role,
};
use provider_manager::Provider;
use crate::{InferenceError, InferenceRequest, InferenceResponse};
use prompt_builder::PromptBuilder;
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
    prompt_builder: PromptBuilder,
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
	    prompt_builder: PromptBuilder::new(),
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
        let history = self.memory.recent(&request.user_id);

        for (prompt, response) in history {

            self.context.add(
             context::Message {

               role: context::Role::User,

               content: prompt,

             }
            );
	    

            self.context.add(
             context::Message {

            	role: context::Role::Assistant,

            	content: response,

             }
    	 );

       }
       self.context.add(
           Message {
        	role: Role::User,
        	content: request.prompt.clone(),
         }
       );

 	self.context.add(
           context::Message {

        	role: context::Role::User,

       		 content: request.prompt.clone(),

    	   }
	);
	let messages = self.context.window();

        let prompt = self
    	 	.prompt_builder
    		.build(&messages);

        //let context_window = self.context.window();
        //--------------------------------------------------
        // STEP 2
        //--------------------------------------------------

        let candidates = self.model_registry.models_for(capability);

        //--------------------------------------------------
        // STEP 3
        //--------------------------------------------------

        let ranked = self.benchmark_engine.rank(candidates);

        //--------------------------------------------------
        // STEP 4
        //--------------------------------------------------

        let available = self.resource_manager.filter(ranked);

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

        let ollama = self.provider_manager.ollama();

	let response = ollama
    		.generate(&prompt)
    		.map_err(|e| InferenceError::ExecutionFailed(e.to_string()))?;
        self.context.add(
    	     Message {
        	role: Role::Assistant,
        	content: response.clone(),
    	    }
	);
        //--------------------------------------------------
        // STEP 8
        //--------------------------------------------------

        self.memory
            .store_interaction(&request.user_id, &request.prompt, &response);

        Ok(InferenceResponse {
            model: selected.name().to_string(),

            output: response,
        })
    }
}
