use crate::CoordinatorError;
use crate::{
    //CoordinatorError,
    //Executor,
    InferenceResult,
    InferenceTask,
    // Planner,
};

use crate::executor::Executor;
use crate::planner::Planner;
pub struct Pipeline {
    planner: Planner,
    executor: Executor,
}

impl Pipeline {
    pub fn new() -> Self {
        Self {
            planner: Planner::new(),
            executor: Executor::new(),
        }
    }

    pub fn execute(&mut self, task: InferenceTask) -> Result<InferenceResult, CoordinatorError> {
        let plan = self.planner.plan(&task)?;

        let result = self.executor.execute(&plan, task)?;

        Ok(crate::InferenceResult {
            output: result.output,
            model: result.model,
            provider: plan.selection.provider.clone(),
        })
    }
}
