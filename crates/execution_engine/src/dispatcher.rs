use std::collections::HashMap;

use crate::{
    ExecutionRequest, ExecutionResult, ToolExecutor,
    executors::{
        FilesystemExecutor, MemoryExecutor, ReasoningExecutor, ShellExecutor, WebExecutor,
    },
};

pub struct Dispatcher {
    executors: HashMap<String, Box<dyn ToolExecutor>>,
}

impl Dispatcher {
    pub fn new() -> Self {
        let mut dispatcher = Self {
            executors: HashMap::new(),
        };

        dispatcher.register("filesystem", Box::new(FilesystemExecutor));
        dispatcher.register("shell", Box::new(ShellExecutor));
        dispatcher.register("web", Box::new(WebExecutor));
        dispatcher.register("memory", Box::new(MemoryExecutor));
        dispatcher.register("reasoning", Box::new(ReasoningExecutor));

        dispatcher
    }

    pub fn register(&mut self, target: impl Into<String>, executor: Box<dyn ToolExecutor>) {
        self.executors.insert(target.into(), executor);
    }

    pub fn dispatch(&self, request: &ExecutionRequest) -> ExecutionResult {
        match self.executors.get(&request.target) {
            Some(executor) => executor.execute(request),
            None => {
                ExecutionResult::failure(format!("No executor registered for '{}'", request.target))
            }
        }
    }
}
