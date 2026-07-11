use crate::{AgentAction, ExecutionPlan, PlanBuilder};

pub struct AgentPlanner;

impl AgentPlanner {
    pub fn new() -> Self {
        Self
    }

    pub fn create_plan(&self, prompt: &str) -> ExecutionPlan {
        let mut builder = PlanBuilder::new();

        if let Some(command) = prompt.strip_prefix("shell:") {
            let tool = builder.add_step(AgentAction::UseTool, "shell", command.trim());

            builder.add_step_after(&tool, AgentAction::Respond, "", "");

            return builder.build();
        }

        if let Some(path) = prompt.strip_prefix("read:") {
            let tool = builder.add_step(AgentAction::UseTool, "filesystem", path.trim());

            builder.add_step_after(&tool, AgentAction::Respond, "", "");

            return builder.build();
        }

        if let Some(query) = prompt.strip_prefix("web:") {
            let tool = builder.add_step(AgentAction::UseTool, "web", query.trim());

            builder.add_step_after(&tool, AgentAction::Respond, "", "");

            return builder.build();
        }

        builder.add_step(AgentAction::Respond, "", "");

        builder.build()
    }
}
