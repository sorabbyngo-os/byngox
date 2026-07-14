use std::fs;

use crate::ExecutionResult;

pub fn execute(path: &str) -> ExecutionResult {
    match fs::create_dir_all(path) {
        Ok(_) => ExecutionResult::success("directory created"),
        Err(e) => ExecutionResult::failure(e.to_string()),
    }
}
