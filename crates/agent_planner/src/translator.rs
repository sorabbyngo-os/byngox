use reasoning_engine::Goal;

use capability_registry::{CapabilityRegistry, ProviderRegistry, load_default_providers};

use crate::{AgentAction, ExecutionPlan, PlanBuilder, ToolClassifier};

pub struct GoalTranslator {
    providers: ProviderRegistry,
}

impl GoalTranslator {
    pub fn new() -> Self {
        let mut providers = ProviderRegistry::new();

        capability_registry::load_default_providers(&mut providers);

        Self { providers }
    }

    pub fn translate(&self, goals: &[Goal]) -> ExecutionPlan {
        let mut builder = PlanBuilder::new();

        for goal in goals {
            let capability = ToolClassifier::classify(&goal.description);

            let provider = self
                .providers
                .resolve(capability)
                .expect("provider not registered");

            let tool = builder.add_step(
                AgentAction::UseTool,
                provider.target.clone(),
                &goal.description,
            );

            builder.add_step_after(&tool, AgentAction::Respond, "", "");
        }

        builder.build()
    }
}
