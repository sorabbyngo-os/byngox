use std::time::{Duration, SystemTime};

use serde::{Deserialize, Serialize};

use crate::ExecutionState;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionRecord {
    pub step_id: String,

    pub runtime: String,

    pub target: String,

    pub operation: String,

    pub state: ExecutionState,

    pub started: SystemTime,

    pub duration: Duration,

    pub success: bool,

    pub output: String,
}
