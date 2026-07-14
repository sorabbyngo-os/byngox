use crate::{Dispatcher, ExecutionContext, ExecutionRequest, ExecutionResult, Runtime};

pub struct LocalRuntime {
    dispatcher: Dispatcher,
}

impl LocalRuntime {
    pub fn new() -> Self {
        Self {
            dispatcher: Dispatcher::new(),
        }
    }

    pub fn dispatcher(&self) -> &Dispatcher {
        &self.dispatcher
    }
}

impl Default for LocalRuntime {
    fn default() -> Self {
        Self::new()
    }
}

impl Runtime for LocalRuntime {
    fn name(&self) -> &'static str {
        "local"
    }

    fn execute(&self, _context: &ExecutionContext, request: &ExecutionRequest) -> ExecutionResult {
        self.dispatcher.dispatch(request)
    }
}
