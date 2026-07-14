use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ExecutionEvent {
    ExecutionStarted,

    ExecutionFinished,

    StepQueued { step_id: String },

    StepStarted { step_id: String },

    StepCompleted { step_id: String },

    StepFailed { step_id: String },

    RuntimeSelected { runtime: String },
}
