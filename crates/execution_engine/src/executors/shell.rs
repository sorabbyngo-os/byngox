use crate::{ExecutionRequest, ExecutionResult, ToolExecutor};

pub struct ShellExecutor;

impl ToolExecutor for ShellExecutor {
    fn execute(&self, request: &ExecutionRequest) -> ExecutionResult {
        ExecutionResult::success(format!("Shell executor received: {}", request.instruction))
    }
}
