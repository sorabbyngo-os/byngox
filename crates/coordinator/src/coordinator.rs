use crate::CoordinatorError;
use crate::{
    //CoordinatorError,
    InferenceResult,
    InferenceTask,
    //Pipeline,
};

use crate::pipeline::Pipeline;
pub struct InferenceCoordinator {
    pipeline: Pipeline,
}

impl InferenceCoordinator {
    pub fn new() -> Self {
        Self {
            pipeline: Pipeline::new(),
        }
    }

    pub fn execute(&mut self, task: InferenceTask) -> Result<InferenceResult, CoordinatorError> {
        self.pipeline.execute(task)
    }
}
