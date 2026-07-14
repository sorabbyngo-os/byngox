use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ExecutionState {
    Pending,
    Ready,
    Running,
    Completed,
    Failed,
    Cancelled,
    Skipped,
}
