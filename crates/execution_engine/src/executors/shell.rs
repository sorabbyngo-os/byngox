use std::process::Command;

use crate::{ExecutionRequest, ExecutionResult, ToolExecutor};

pub struct ShellExecutor;

impl ToolExecutor for ShellExecutor {
    fn execute(&self, request: &ExecutionRequest) -> ExecutionResult {
        let command = request.input.trim();

        if command.is_empty() {
            return ExecutionResult::failure("empty shell command");
        }

        let output = Command::new("sh").arg("-c").arg(command).output();

        match output {
            Ok(result) => {
                if result.status.success() {
                    ExecutionResult::success(String::from_utf8_lossy(&result.stdout).to_string())
                } else {
                    ExecutionResult::failure(String::from_utf8_lossy(&result.stderr).to_string())
                }
            }

            Err(e) => ExecutionResult::failure(e.to_string()),
        }
    }
}
