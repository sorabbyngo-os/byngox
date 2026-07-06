#[derive(Clone, Debug)]
pub struct InferenceRequest {
    pub capability: String,
    pub prompt: String,
    pub user_id: String,
}
