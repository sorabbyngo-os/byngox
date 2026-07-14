use std::fs::OpenOptions;
use std::io::Write;

use crate::ExecutionResult;

pub fn execute(args: &str) -> ExecutionResult {
    let mut parts = args.splitn(2, ' ');

    let path = parts.next().unwrap_or("");
    let contents = parts.next().unwrap_or("");

    match OpenOptions::new().append(true).create(true).open(path) {
        Ok(mut file) => {
            if let Err(e) = writeln!(file, "{}", contents) {
                return ExecutionResult::failure(e.to_string());
            }

            ExecutionResult::success("appended")
        }

        Err(e) => ExecutionResult::failure(e.to_string()),
    }
}
