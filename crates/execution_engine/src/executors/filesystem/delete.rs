use std::fs;

use crate::ExecutionResult;

pub fn execute(path: &str) -> ExecutionResult {
    match fs::remove_file(path) {
        Ok(_) => ExecutionResult::success("deleted"),
        Err(e) => ExecutionResult::failure(e.to_string()),
    }
}
