use crate::{ExecutionRequest, ExecutionResult, ToolExecutor};

pub struct MemoryExecutor;

impl ToolExecutor for MemoryExecutor {
    fn execute(&self, request: &ExecutionRequest) -> ExecutionResult {
        ExecutionResult::success(format!("Memory executor received: {}", request.instruction))
    }
}
