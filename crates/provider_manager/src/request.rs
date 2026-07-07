#[derive(Clone, Debug)]

pub struct InferenceRequest {
    pub model: String,

    pub prompt: String,
}
