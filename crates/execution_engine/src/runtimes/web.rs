use crate::{ExecutionContext, ExecutionRequest, ExecutionResult, Runtime};

pub struct WebRuntime;

impl Runtime for WebRuntime {
    fn name(&self) -> &'static str {
        "web"
    }

    fn execute(&self, _: &ExecutionContext, request: &ExecutionRequest) -> ExecutionResult {
        ExecutionResult {
            success: true,
            output: format!("web received '{}'", request.instruction),
        }
    }
}
