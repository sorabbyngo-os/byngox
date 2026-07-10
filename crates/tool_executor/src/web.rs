use reqwest::blocking::Client;

use crate::{
    Tool,
    ToolError,
    ToolResult,
};

pub struct WebTool {
    client: Client,
}

impl WebTool {
    pub fn new() -> Self {
        Self {
            client: Client::new(),
        }
    }
}

impl Tool for WebTool {
    fn name(&self) -> &'static str {
        "web"
    }

    fn description(&self) -> &'static str {
        "Downloads text from a URL."
    }

    fn execute(
        &self,
        input: &str,
    ) -> Result<ToolResult, ToolError> {

        let response = self
            .client
            .get(input)
            .send()
            .map_err(|e| ToolError::ExecutionFailed(e.to_string()))?;

        let body = response
            .text()
            .map_err(|e| ToolError::ExecutionFailed(e.to_string()))?;

        Ok(ToolResult {
            success: true,
            output: body,
        })
    }
}
