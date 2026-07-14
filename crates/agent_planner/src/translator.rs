use reasoning_engine::Goal;

use crate::{AgentAction, ExecutionPlan, PlanBuilder};

pub struct GoalTranslator;

impl GoalTranslator {
    pub fn new() -> Self {
        Self
    }

    pub fn translate(&self, goals: &[Goal]) -> ExecutionPlan {
        let mut builder = PlanBuilder::new();

        for goal in goals {
            // Temporary heuristic until capability routing is added.
            let (target, input) = if goal.description.to_lowercase().starts_with("read") {
                ("filesystem", goal.description.clone())
            } else if goal.description.to_lowercase().starts_with("web") {
                ("web", goal.description.clone())
            } else if goal.description.to_lowercase().starts_with("shell") {
                ("shell", goal.description.clone())
            } else {
                ("reasoning", goal.description.clone())
            };

            let tool_step = builder.add_step("local", AgentAction::UseTool, target, input);

            builder.add_step_after(&tool_step, "local", AgentAction::Respond, "", "");
        }

        builder.build()
    }
}

impl Default for GoalTranslator {
    fn default() -> Self {
        Self::new()
    }
}
