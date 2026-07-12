use crate::{ExecutionContext, ExecutionRequest, ExecutionResult, Runtime};

pub struct ReasoningRuntime;

impl Runtime for ReasoningRuntime {
    fn name(&self) -> &'static str {
        "reasoning"
    }

    fn execute(&self, _: &ExecutionContext, request: &ExecutionRequest) -> ExecutionResult {
        ExecutionResult {
            success: true,
            output: format!("reasoning received '{}'", request.instruction),
        }
    }
}
