use std::fs;

use crate::ExecutionResult;

pub fn execute(args: &str) -> ExecutionResult {
    let mut parts = args.split_whitespace();

    let src = parts.next().unwrap_or("");
    let dst = parts.next().unwrap_or("");

    match fs::rename(src, dst) {
        Ok(_) => ExecutionResult::success("moved"),
        Err(e) => ExecutionResult::failure(e.to_string()),
    }
}
