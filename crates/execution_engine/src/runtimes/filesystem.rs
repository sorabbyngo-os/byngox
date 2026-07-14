use crate::{ExecutionContext, ExecutionRequest, ExecutionResult, Runtime};

pub struct FilesystemRuntime;

impl Runtime for FilesystemRuntime {
    fn name(&self) -> &'static str {
        "filesystem"
    }

    fn execute(&self, _: &ExecutionContext, request: &ExecutionRequest) -> ExecutionResult {
        ExecutionResult {
            success: true,
            output: format!("filesystem received '{}'", request.input),
        }
    }
}
