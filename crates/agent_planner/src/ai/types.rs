use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum PlannerAction {
    Tool,
    Respond,
    Finish,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlannerStep {
    pub action: PlannerAction,

    #[serde(default)]
    pub tool: Option<String>,

    #[serde(default)]
    pub input: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlannerOutput {
    pub steps: Vec<PlannerStep>,
}
