use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct OllamaTagsResponse {
    pub models: Vec<OllamaModel>,
}

#[derive(Debug, Deserialize)]
pub struct OllamaModel {
    pub name: String,
    pub model: String,

    pub modified_at: Option<String>,

    pub size: Option<u64>,

    pub digest: Option<String>,

    pub details: OllamaDetails,

    #[serde(default)]
    pub capabilities: Vec<String>,
}

#[derive(Debug, Deserialize)]
pub struct OllamaDetails {
    pub parent_model: Option<String>,

    pub format: Option<String>,

    pub family: Option<String>,

    #[serde(default)]
    pub families: Vec<String>,

    pub parameter_size: Option<String>,

    pub quantization_level: Option<String>,

    pub context_length: Option<usize>,

    pub embedding_length: Option<usize>,
}
