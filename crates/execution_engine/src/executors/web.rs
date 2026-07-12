use crate::{ExecutionRequest, ExecutionResult, ToolExecutor};

pub struct WebExecutor;

impl ToolExecutor for WebExecutor {
    fn execute(&self, request: &ExecutionRequest) -> ExecutionResult {
        ExecutionResult::success(format!("Web executor received: {}", request.instruction))
    }
}
