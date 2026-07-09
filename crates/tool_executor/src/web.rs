use crate::{
    Tool,
    ToolError,
    ToolResult,
};

pub struct WebTool;

impl WebTool {
    pub fn new() -> Self {
        Self
    }
}

impl Tool for WebTool {
    fn name(&self) -> &'static str {
        "web"
    }

    fn description(&self) -> &'static str {
        "Placeholder web tool"
    }

    fn execute(
        &self,
        input: &str,
    ) -> Result<ToolResult, ToolError> {
        Ok(ToolResult {
            success: true,
            output: format!(
                "Web tool not yet implemented. Request: {}",
                input
            ),
        })
    }
}
