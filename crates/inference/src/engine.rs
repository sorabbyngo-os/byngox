//use tool_executor::{
  //  FilesystemTool,
    //ShellTool,
    //WebTool,
//};
//use tool_executor::{
  //  ToolExecutor,
    //FilesystemTool,
   // ShellTool,
   // WebTool,
//};
use task_runtime::TaskRuntime;
use crate::{InferenceError, InferenceRequest, InferenceResponse};
use benchmark_engine::BenchmarkEngine;
use capability_registry::CapabilityRegistry;
use context::{ContextManager, Message, Role};
use memory::MemoryManager;
use model_registry::ModelRegistry;
use model_router::ModelRouter;
use prompt_builder::PromptBuilder;
use provider_manager::{OllamaProvider, ProviderManager};
use resource_manager::ResourceManager;
use agent_planner::AgentPlanner;

pub struct InferenceEngine {
    capability_registry: CapabilityRegistry,
    model_registry: ModelRegistry,
    benchmark_engine: BenchmarkEngine,
    resource_manager: ResourceManager,
    router: ModelRouter,
    provider_manager: ProviderManager,
    planner: AgentPlanner,
    task_runtime: TaskRuntime,
    memory: MemoryManager,
    context: ContextManager,
    prompt_builder: PromptBuilder,
}

impl InferenceEngine {
    pub fn new() -> Self {
        let mut provider_manager = ProviderManager::new();

        provider_manager.register(Box::new(OllamaProvider::new()));

        let mut model_registry = ModelRegistry::new();

        let discovered = provider_manager
            .discover_models()
            .expect("failed to discover models");

        for model in discovered {
            model_registry.register(model);
        }
	
	//let tool_executor = ToolExecutor::new();
	let task_runtime = TaskRuntime::new();
//	let mut tool_executor = ToolExecutor::new();

//	tool_executor
    //		.registry_mut()
  //  		.register(FilesystemTool::new());

//	tool_executor
    //		.registry_mut()
  //  		.register(ShellTool::new());

//	tool_executor
  //  		.registry_mut()
//    		.register(WebTool::new());        


        Self {
            capability_registry: CapabilityRegistry::new(),
            model_registry,
            benchmark_engine: BenchmarkEngine::new(),
            resource_manager: ResourceManager::new(),
            router: ModelRouter::new(),
            provider_manager,
            memory: MemoryManager::new(),
	    task_runtime,
	    planner: AgentPlanner::new(),
            context: ContextManager::new(),
            prompt_builder: PromptBuilder::new(),
        }
    }
   
 //   fn execute_tool(
   //    &self,
     //  tool: &str,
       //input: &str,
   // ) -> Result<String, InferenceError> {

     //  let result = self
       //   .tool_executor
        //  .execute(tool, input)
         // .map_err(|e| {
           // 	   InferenceError::ExecutionFailed(
             //   	e.to_string()
            //	   )
        //	})?;
//
  //  	Ok(result.output)
  //  }

    //fn dispatch_tool(
    //  &self,
    //  prompt: &str,
    //) -> Result<Option<String>, InferenceError> {

    //  if let Some(command) = prompt.strip_prefix("shell:") {
      //  return self
        //    .execute_tool("shell", command.trim())
          //  .map(Some);
     // }

     // if let Some(path) = prompt.strip_prefix("read:") {
      //  return self
        //    .execute_tool("filesystem", path.trim())
          //  .map(Some);
     // }

     // if let Some(query) = prompt.strip_prefix("web:") {
      //  return self
        //    .execute_tool("web", query.trim())
          //  .map(Some);
     // }

      //Ok(None)
   // }   

    pub fn execute(
        &mut self,
        request: InferenceRequest,
    ) -> Result<InferenceResponse, InferenceError> {
        let capability = &request.capability;
	let plan = self.planner.create_plan(&request.prompt);
        let history = self.memory.recent(&request.user_id);

        for (prompt, response) in history {
            self.context.add(Message {
                role: Role::User,
                content: prompt,
            });

            self.context.add(Message {
                role: Role::Assistant,
                content: response,
            });
        }

        self.context.add(Message {
            role: Role::User,
            content: request.prompt.clone(),
        });

        let messages = self.context.window();

	let mut prompt = self
    		.prompt_builder
    		.build(&messages);

	let memories = self.memory.search_memory(
 	   &request.user_id,
   	   &request.prompt,
	);

	if !memories.is_empty() {

          prompt.push_str("\n\nRelevant Memories:\n");

          for memory in memories {

        	prompt.push_str("- ");

        	prompt.push_str(&memory);

        	prompt.push('\n');
    	  }
	}

//	for step in &plan.steps {
//
  //  		match step.action {
//
  //      	  AgentAction::UseTool => {
//
        //    	    let output = self.execute_tool(
      //          	&step.target,
    //            	&step.input,
  //          	    )?;
//
      //      	    prompt.push_str("\n\nTool Output:\n");
    //                prompt.push_str(&output);
  //      	  }
//
  //      	  AgentAction::Respond => {}
//
  //      	  AgentAction::Finish => break,
    //	       }
//	}	

	let runtime_result = self
 	   .task_runtime
    	   .execute(plan)
    	   .map_err(|e| {
        	InferenceError::ExecutionFailed(e.to_string())
    	  })?;

	if runtime_result.success {

    		prompt.push_str("\n\nTool Output:\n");

    		prompt.push_str(&runtime_result.output);
	}


	//let prompt = if let Some(tool_output) = self.dispatch_tool(&prompt)? {

    	//	format!(
        //		"{}\n\nTool Output:\n{}",
      //		prompt,
        //		tool_output,
    	//	)
	//} else {
    	//	prompt

//	};
//	
//	for step in &plan.steps {
//
 //	   match step.action {
//
  //      	AgentAction::UseTool => {
//
    //        	  let output = self.execute_tool(
  //             		 &step.target,
      //         		 &step.input,
        //    	  )?;
	
//	let runtime_result = self
  //  	 .task_runtime
    //	 .execute(plan)
    //	 .map_err(|e| {
      //  	InferenceError::ExecutionFailed(e.to_string())
    //	})?;

//	if runtime_result.success {
//
  //  	prompt.push_str("\n\nTool Output:\n");

    //	prompt.push_str(&runtime_result.output);
//	}
//
    //        	  prompt.push_str("\n\nTool Output:\n");
  //          	  prompt.push_str(&output);
      //  	}
//
  //      	AgentAction::Respond => {}
//
  //      	AgentAction::Finish => break,
    //	    }
//	  }


        let candidates = self.model_registry.models_for(capability);
        let ranked = self.benchmark_engine.rank(candidates);
        let available = self.resource_manager.filter(ranked);

        let selected = self
            .router
            .select(available)
            .ok_or(InferenceError::NoModelAvailable)?;

        let provider = self
            .provider_manager
            .providers()
            .first()
            .ok_or(InferenceError::ProviderNotFound)?;

        let response = provider
            .generate(&selected.model, &prompt)
            .map_err(|e| InferenceError::ExecutionFailed(e.to_string()))?;

        self.memory
            .store_interaction(&request.user_id, &request.prompt, &response);
	self.memory.store_memory(
    	  &request.user_id,
    	  format!(
        	"User: {}\nAssistant: {}",
        	request.prompt,
        	response
    	  ),
	);


        Ok(InferenceResponse {
            model: selected.name().to_string(),
            output: response,
        })
    }

}
