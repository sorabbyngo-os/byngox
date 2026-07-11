use serde::{Deserialize, Serialize};

use crate::AgentAction;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub id: String,
    pub description: String,
    pub action: AgentAction,
    pub target: String,
    pub input: String,
    pub dependencies: Vec<String>,
}

impl Task {
    pub fn new(
        id: impl Into<String>,
        description: impl Into<String>,
        action: AgentAction,
        target: impl Into<String>,
        input: impl Into<String>,
    ) -> Self {
        Self {
            id: id.into(),
            description: description.into(),
            action,
            target: target.into(),
            input: input.into(),
            dependencies: Vec::new(),
        }
    }

    pub fn depends_on(mut self, dependency: impl Into<String>) -> Self {
        self.dependencies.push(dependency.into());
        self
    }
}
