use reasoning_engine::Goal;

use crate::{AgentAction, CapabilityResolver, ExecutionPlan, PlanBuilder, ToolClassifier};

pub struct GoalTranslator;

impl GoalTranslator {
    pub fn new() -> Self {
        Self
    }

    pub fn translate(&self, goals: &[Goal]) -> ExecutionPlan {
        let mut builder = PlanBuilder::new();

        for goal in goals {
            let capability = ToolClassifier::classify(&goal.description);

            let target = CapabilityResolver::resolve(capability);

            let tool = builder.add_step(AgentAction::UseTool, target, &goal.description);

            builder.add_step_after(&tool, AgentAction::Respond, "", "");
        }

        builder.build()
    }
}
