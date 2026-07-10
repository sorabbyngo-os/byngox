use std::process::Command;

use crate::{
    Tool,
    ToolError,
    ToolResult,
};

pub struct ShellTool;

impl ShellTool {
    pub fn new() -> Self {
        Self
    }
}

impl Tool for ShellTool {
    fn name(&self) -> &'static str {
        "shell"
    }

    fn description(&self) -> &'static str {
        "Executes shell commands."
    }

    fn execute(
        &self,
        input: &str,
    ) -> Result<ToolResult, ToolError> {

        let output = Command::new("sh")
            .arg("-c")
            .arg(input)
            .output()
            .map_err(|e| ToolError::ExecutionFailed(e.to_string()))?;

        if output.status.success() {
            Ok(ToolResult {
                success: true,
                output: String::from_utf8_lossy(&output.stdout).to_string(),
            })
        } else {
            Err(ToolError::ExecutionFailed(
                String::from_utf8_lossy(&output.stderr).to_string(),
            ))
        }
    }
}
