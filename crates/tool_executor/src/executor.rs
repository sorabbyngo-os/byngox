use crate::{
    ToolError,
    ToolRegistry,
    ToolResult,
};

pub struct ToolExecutor {
    registry: ToolRegistry,
}

impl ToolExecutor {
    pub fn new() -> Self {
        Self {
            registry: ToolRegistry::new(),
        }
    }

    pub fn registry(&self) -> &ToolRegistry {
        &self.registry
    }

    pub fn registry_mut(&mut self) -> &mut ToolRegistry {
        &mut self.registry
    }

    pub fn execute(
        &self,
        tool: &str,
        input: &str,
    ) -> Result<ToolResult, ToolError> {
        let tool = self
            .registry
            .get(tool)
            .ok_or_else(|| ToolError::ToolNotFound(tool.to_string()))?;

        tool.execute(input)
    }
}
