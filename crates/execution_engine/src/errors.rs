use thiserror::Error;

#[derive(Debug, Error)]
pub enum ExecutionError {
    #[error("runtime not found")]
    RuntimeNotFound,

    #[error("execution failed: {0}")]
    Failed(String),
}
