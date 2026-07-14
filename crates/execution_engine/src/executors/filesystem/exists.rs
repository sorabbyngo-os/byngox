use std::path::Path;

use crate::ExecutionResult;

pub fn execute(path: &str) -> ExecutionResult {
    ExecutionResult::success(Path::new(path).exists().to_string())
}
