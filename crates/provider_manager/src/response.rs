use serde::Deserialize;

#[derive(Deserialize)]
pub struct OllamaResponse {
    pub response: String,
}
