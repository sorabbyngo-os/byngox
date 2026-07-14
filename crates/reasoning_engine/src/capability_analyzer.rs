use ai_core::Capability;

use crate::Goal;

pub struct CapabilityAnalyzer;

impl CapabilityAnalyzer {
    pub fn new() -> Self {
        Self
    }
    pub fn detect(&self, goal: &Goal) -> Vec<Capability> {
    let text = goal.description.to_lowercase();

    let mut capabilities = Vec::new();

    if text.starts_with("read")
        || text.starts_with("write")
        || text.starts_with("copy")
        || text.starts_with("delete")
        || text.starts_with("move")
    {
        capabilities.push(Capability::Coding);
    }

    if text.starts_with("web")
        || text.starts_with("search")
        || text.starts_with("browse")
    {
        capabilities.push(Capability::Reasoning);
    }

    if text.starts_with("shell")
        || text.starts_with("run")
        || text.starts_with("execute")
    {
        capabilities.push(Capability::Coding);
    }

    if capabilities.is_empty() {
        capabilities.push(Capability::Reasoning);
    }

    capabilities
  }

}
