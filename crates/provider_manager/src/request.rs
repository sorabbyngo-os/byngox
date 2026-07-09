use serde::Serialize;

#[derive(Serialize)]
pub struct OllamaRequest {
    pub model: String,

    pub prompt: String,

    pub stream: bool,
}
