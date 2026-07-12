use crate::{ExecutionRequest, ExecutionResult};

pub trait ToolExecutor: Send + Sync {
    fn execute(&self, request: &ExecutionRequest) -> ExecutionResult;
}
