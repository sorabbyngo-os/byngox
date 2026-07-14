use std::fs;

use crate::ExecutionResult;

pub fn execute(path: &str) -> ExecutionResult {
    match fs::metadata(path) {
        Ok(meta) => {
            let output = format!(
                "size={} readonly={} is_file={} is_dir={}",
                meta.len(),
                meta.permissions().readonly(),
                meta.is_file(),
                meta.is_dir(),
            );

            ExecutionResult::success(output)
        }

        Err(e) => ExecutionResult::failure(e.to_string()),
    }
}
