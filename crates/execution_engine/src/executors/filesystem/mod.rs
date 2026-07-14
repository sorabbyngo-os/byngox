pub mod append;
pub mod copy;
pub mod create_dir;
pub mod delete;
pub mod exists;
pub mod list;
pub mod metadata;
pub mod move_file;
pub mod read;
pub mod write;

use crate::{ExecutionRequest, ExecutionResult, ToolExecutor};

pub struct FilesystemExecutor;

impl ToolExecutor for FilesystemExecutor {
    fn execute(&self, request: &ExecutionRequest) -> ExecutionResult {
        let mut parts = request.input.splitn(2, ' ');

        let operation = parts.next().unwrap_or("");
        let argument = parts.next().unwrap_or("");

        match operation {
            "read" => read::execute(argument),
            "write" => write::execute(argument),
            "append" => append::execute(argument),
            "copy" => copy::execute(argument),
            "move" => move_file::execute(argument),
            "delete" => delete::execute(argument),
            "mkdir" => create_dir::execute(argument),
            "list" => list::execute(argument),
            "exists" => exists::execute(argument),
            "metadata" => metadata::execute(argument),

            _ => ExecutionResult::failure(format!("Unknown filesystem operation '{}'", operation)),
        }
    }
}
