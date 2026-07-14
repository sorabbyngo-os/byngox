use crate::{ExecutionContext, ExecutionRequest, ExecutionResult, Runtime};

pub struct MemoryRuntime;

impl Runtime for MemoryRuntime {
    fn name(&self) -> &'static str {
        "memory"
    }

    fn execute(&self, _: &ExecutionContext, request: &ExecutionRequest) -> ExecutionResult {
        ExecutionResult {
            success: true,
            output: format!("memory received '{}'", request.input),
        }
    }
}
