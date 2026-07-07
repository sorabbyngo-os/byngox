#[derive(Debug)]
pub enum CoordinatorError {
    CapabilityNotFound,

    NoModelAvailable,

    ExecutionFailed(String),
}

impl std::fmt::Display for CoordinatorError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::CapabilityNotFound => write!(f, "Capability not found"),

            Self::NoModelAvailable => write!(f, "No model available"),

            Self::ExecutionFailed(msg) => write!(f, "Execution failed: {}", msg),
        }
    }
}

impl std::error::Error for CoordinatorError {}
impl From<inference::InferenceError> for CoordinatorError {
    fn from(err: inference::InferenceError) -> Self {
        CoordinatorError::ExecutionFailed(err.to_string())
    }
}
