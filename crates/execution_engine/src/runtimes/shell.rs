use crate::{ExecutionContext, ExecutionRequest, ExecutionResult, Runtime};

pub struct ShellRuntime;

impl Runtime for ShellRuntime {
    fn name(&self) -> &'static str {
        "shell"
    }

    fn execute(&self, _: &ExecutionContext, request: &ExecutionRequest) -> ExecutionResult {
        ExecutionResult {
            success: true,
            output: format!("shell received '{}'", request.input),
        }
    }
}
