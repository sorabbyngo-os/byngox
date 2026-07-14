use std::fs;

use crate::ExecutionResult;

pub fn execute(path: &str) -> ExecutionResult {
    match fs::read_dir(path) {
        Ok(entries) => {
            let mut output = String::new();

            for entry in entries.flatten() {
                output.push_str(&format!("{}\n", entry.file_name().to_string_lossy()));
            }

            ExecutionResult::success(output)
        }

        Err(e) => ExecutionResult::failure(e.to_string()),
    }
}
