use crate::{ExecutionRequest, ExecutionResult, ToolExecutor};

pub struct FilesystemExecutor;

impl ToolExecutor for FilesystemExecutor {
    fn execute(&self, request: &ExecutionRequest) -> ExecutionResult {
        ExecutionResult::success(format!(
            "Filesystem executor received: {}",
            request.instruction
        ))
    }
}
