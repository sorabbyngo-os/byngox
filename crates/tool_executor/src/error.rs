use std::fmt;

#[derive(Debug)]
pub enum ToolError {
    ToolNotFound(String),
    ExecutionFailed(String),
    InvalidInput(String),
}

impl fmt::Display for ToolError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ToolError::ToolNotFound(name) => {
                write!(f, "Tool not found: {}", name)
            }

            ToolError::ExecutionFailed(message) => {
                write!(f, "Tool execution failed: {}", message)
            }

            ToolError::InvalidInput(message) => {
                write!(f, "Invalid tool input: {}", message)
            }
        }
    }
}

impl std::error::Error for ToolError {}
