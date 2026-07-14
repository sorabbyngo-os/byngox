use std::fs;

use crate::ExecutionResult;

pub fn execute(args: &str) -> ExecutionResult {
    let mut parts = args.splitn(2, ' ');

    let path = parts.next().unwrap_or("");
    let contents = parts.next().unwrap_or("");

    match fs::write(path, contents) {
        Ok(_) => ExecutionResult::success("file written"),
        Err(e) => ExecutionResult::failure(e.to_string()),
    }
}
