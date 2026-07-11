use crate::{AgentAction, Task, TaskGraph};

pub struct TaskGraphBuilder;

impl TaskGraphBuilder {
    pub fn new() -> Self {
        Self
    }

    pub fn build(&self, prompt: &str) -> TaskGraph {
        let mut graph = TaskGraph::new();

        graph.add_task(Task::new(
            "step-1",
            prompt,
            AgentAction::Respond,
            "",
            prompt,
        ));

        graph
    }
}
