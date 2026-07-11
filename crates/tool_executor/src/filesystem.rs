use std::fs;

use crate::{Tool, ToolError, ToolResult};

pub struct FilesystemTool;

impl FilesystemTool {
    pub fn new() -> Self {
        Self
    }
}

impl Tool for FilesystemTool {
    fn name(&self) -> &'static str {
        "filesystem"
    }

    fn description(&self) -> &'static str {
        "Read files from the local filesystem"
    }

    fn execute(&self, input: &str) -> Result<ToolResult, ToolError> {
        let file_contents =
            fs::read_to_string(input).map_err(|e| ToolError::ExecutionFailed(e.to_string()))?;

        Ok(ToolResult {
            success: true,
            output: file_contents,
        })
    }
}
