use crate::{
    AgentAction,
    ExecutionPlan,
    PlanStep,
};

pub struct AgentPlanner;

impl AgentPlanner {

    pub fn new() -> Self {
        Self
    }

    pub fn create_plan(
        &self,
        prompt: &str,
    ) -> ExecutionPlan {

        let mut plan = ExecutionPlan::new();

        if let Some(command) = prompt.strip_prefix("shell:") {

            plan.add_step(
                PlanStep {
                    action: AgentAction::UseTool,
                    target: "shell".to_string(),
                    input: command.trim().to_string(),
                }
            );

            plan.add_step(
                PlanStep {
                    action: AgentAction::Respond,
                    target: String::new(),
                    input: String::new(),
                }
            );

            return plan;
        }

        if let Some(path) = prompt.strip_prefix("read:") {

            plan.add_step(
                PlanStep {
                    action: AgentAction::UseTool,
                    target: "filesystem".to_string(),
                    input: path.trim().to_string(),
                }
            );

            plan.add_step(
                PlanStep {
                    action: AgentAction::Respond,
                    target: String::new(),
                    input: String::new(),
                }
            );

            return plan;
        }

        if let Some(query) = prompt.strip_prefix("web:") {

            plan.add_step(
                PlanStep {
                    action: AgentAction::UseTool,
                    target: "web".to_string(),
                    input: query.trim().to_string(),
                }
            );

            plan.add_step(
                PlanStep {
                    action: AgentAction::Respond,
                    target: String::new(),
                    input: String::new(),
                }
            );

            return plan;
        }

        plan.add_step(
            PlanStep {
                action: AgentAction::Respond,
                target: String::new(),
                input: String::new(),
            }
        );

        plan
    }

}
