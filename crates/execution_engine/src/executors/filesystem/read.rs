use std::fs;

use crate::ExecutionResult;

pub fn execute(path: &str) -> ExecutionResult {
    match fs::read_to_string(path) {
        Ok(contents) => ExecutionResult::success(contents),
        Err(e) => ExecutionResult::failure(e.to_string()),
    }
}
