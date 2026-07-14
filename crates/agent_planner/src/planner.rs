use reasoning_engine::ReasoningResult;

use crate::translator::GoalTranslator;
use crate::{AgentAction, ExecutionPlan, PlanBuilder};
pub struct AgentPlanner;

impl AgentPlanner {
    pub fn new() -> Self {
        Self
    }

    pub fn create_plan(&self, prompt: &str) -> ExecutionPlan {
        let mut builder = PlanBuilder::new();

        if let Some(command) = prompt.strip_prefix("shell:") {
            let tool = builder.add_step("local", AgentAction::UseTool, "shell", command.trim());

            builder.add_step_after(&tool, "local", AgentAction::Respond, "", "");

            return builder.build();
        }

        if let Some(path) = prompt.strip_prefix("read:") {
            let tool = builder.add_step("local", AgentAction::UseTool, "filesystem", path.trim());

            builder.add_step_after(&tool, "local", AgentAction::Respond, "", "");

            return builder.build();
        }

        if let Some(query) = prompt.strip_prefix("web:") {
            let tool = builder.add_step("local", AgentAction::UseTool, "web", query.trim());

            builder.add_step_after(&tool, "local", AgentAction::Respond, "", "");

            return builder.build();
        }

        builder.add_step("local", AgentAction::Respond, "", "");

        builder.build()
    }

    pub fn create_plan_from_reasoning(&self, reasoning: &ReasoningResult) -> ExecutionPlan {
        GoalTranslator::new().translate(&reasoning.goals)
    }
}

impl Default for AgentPlanner {
    fn default() -> Self {
        Self::new()
    }
}
