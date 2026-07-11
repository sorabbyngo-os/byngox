use crate::{ToolError, ToolResult};

pub trait Tool: Send + Sync {
    fn name(&self) -> &'static str;

    fn description(&self) -> &'static str;

    fn execute(&self, input: &str) -> Result<ToolResult, ToolError>;
}
