use crate::{ToolError, ToolRegistry, ToolResult};

pub struct ToolExecutor {
    registry: ToolRegistry,
}

impl ToolExecutor {
    pub fn new() -> Self {
        Self {
            registry: ToolRegistry::new(),
        }
    }

    pub fn execute(&self, tool_name: &str, input: &str) -> Result<ToolResult, ToolError> {
        let tool = self
            .registry
            .get(tool_name)
            .ok_or(ToolError::ToolNotFound(tool_name.to_string()))?;

        tool.execute(input)
    }
}
