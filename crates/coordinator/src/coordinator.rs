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

        };

        ExecutionPlan {

            selection,

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
