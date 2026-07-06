use std::fmt;

#[derive(Debug)]
pub enum InferenceError {
    CapabilityNotFound,
    NoModelAvailable,
    ProviderNotFound,
    ModelUnavailable,
    ProviderUnavailable,
    ExecutionFailed(String),
}

impl fmt::Display for InferenceError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::CapabilityNotFound => {
                write!(f, "Capability not found")
            }

            Self::NoModelAvailable => {
                write!(f, "No model available")
            }

            Self::ProviderNotFound => {
                write!(f, "Provider not found")
            }

            Self::ModelUnavailable => {
                write!(f, "Model unavailable")
            }

            Self::ProviderUnavailable => {
                write!(f, "Provider unavailable")
            }

            Self::ExecutionFailed(msg) => {
                write!(f, "Execution failed: {}", msg)
            }
        }
    }
}

impl std::error::Error for InferenceError {}
