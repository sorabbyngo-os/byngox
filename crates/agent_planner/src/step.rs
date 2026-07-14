use serde::{Deserialize, Serialize};

use crate::AgentAction;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlanStep {
    /// Unique identifier for this step.
    pub id: String,

    /// Steps that must complete before this step can run.
    pub dependencies: Vec<String>,

    /// What kind of action this step performs.
    pub action: AgentAction,

    /// Target tool/service.
    pub target: String,

    ///a runtime field
    pub runtime: String,

    /// Input passed to the target.
    pub input: String,
}

impl PlanStep {
    pub fn new(
        id: impl Into<String>,
        runtime: impl Into<String>,
        action: AgentAction,
        target: impl Into<String>,
        input: impl Into<String>,
    ) -> Self {
        Self {
            id: id.into(),
            dependencies: Vec::new(),
            action,
            target: target.into(),
            runtime: runtime.into(),
            input: input.into(),
        }
    }

    pub fn depends_on(mut self, dependency: impl Into<String>) -> Self {
        self.dependencies.push(dependency.into());
        self
    }
}
