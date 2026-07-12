use crate::{ExecutionContext, ExecutionRequest, ExecutionResult};

pub trait Runtime: Send + Sync {
    fn name(&self) -> &'static str;

    fn execute(&self, ctx: &ExecutionContext, request: &ExecutionRequest) -> ExecutionResult;
}
