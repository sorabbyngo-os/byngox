use crate::{ExecutionRequest, ExecutionResult, ToolExecutor};

pub struct ReasoningExecutor;

impl ToolExecutor for ReasoningExecutor {
    fn execute(&self, request: &ExecutionRequest) -> ExecutionResult {
        ExecutionResult::success(format!(
            "Reasoning executor received: {}",
            request.instruction
        ))
    }
}
