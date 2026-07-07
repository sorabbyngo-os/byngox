#[derive(Debug)]
pub enum AIError {
    CapabilityNotFound,
    ModelNotFound,
    ProviderNotFound,
    NoModelAvailable,
    ExecutionFailed(String),
}
