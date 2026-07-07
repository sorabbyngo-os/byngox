use crate::{ExecutionPlan, InferenceTask};

use inference::{InferenceEngine, InferenceError, InferenceRequest, InferenceResponse};

pub struct Executor {
    engine: InferenceEngine,
}

impl Executor {
    pub fn new() -> Self {
        Self {
            engine: InferenceEngine::new(),
        }
    }

    pub fn execute(
        &mut self,
        plan: &ExecutionPlan,
        task: InferenceTask,
    ) -> Result<InferenceResponse, InferenceError> {
        let capability = ai_core::Capability::from_str(&plan.capability)
            .ok_or(InferenceError::CapabilityNotFound)?;

        let request = InferenceRequest {
            capability,
            prompt: task.prompt,
            user_id: String::from("system"),
        };

        self.engine.execute(request)
    }
}
