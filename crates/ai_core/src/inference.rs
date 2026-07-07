use crate::Capability;

#[derive(Clone, Debug)]
pub struct InferenceRequest {
    pub user_id: String,
    pub prompt: String,
    pub capability: Capability,
}

#[derive(Clone, Debug)]
pub struct InferenceResponse {
    pub model: String,
    pub output: String,
}
