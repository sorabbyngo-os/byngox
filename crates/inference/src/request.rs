use ai_core::Capability;

#[derive(Clone, Debug)]
pub struct InferenceRequest {
    pub capability: Capability,
    pub prompt: String,
    pub user_id: String,
}
