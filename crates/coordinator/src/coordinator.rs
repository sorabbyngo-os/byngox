use crate::{
    ExecutionPlan,
    InferenceResult,
    InferenceTask,
    ModelSelection,
};

pub struct InferenceCoordinator;

impl InferenceCoordinator {

    pub fn new() -> Self {

        Self

    }

    pub fn plan(

        &self,

        task: &InferenceTask,

    ) -> ExecutionPlan {

      let selection = ModelSelection {
          provider: "local".into(),
          model: format!("best-model-for-{}", task.capability),

          local: true,
          estimated_cost: 0.0,
          latency: 0,
      }; 
        ExecutionPlan {
         selection,

         capability: task.capability.clone(),

         requires_memory: true,

         requires_context: true,
       }

    }

    pub fn execute(

        &self,

        plan: ExecutionPlan,

        _task: InferenceTask,

    ) -> InferenceResult {

        InferenceResult {

            output: String::from("Execution completed"),

            provider: plan.selection.provider,

            model: plan.selection.model,

        }

    }

}
