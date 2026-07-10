use crate::AgentAction;

#[derive(Debug, Clone)]
pub struct PlanStep {
    pub action: AgentAction,
    pub target: String,
    pub input: String,
}
