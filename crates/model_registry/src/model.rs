#[derive(Debug, Clone)]
pub enum ModelType {
    LLM,
    Vision,
    Audio,
    Multimodal,
    Embedding,
    OCR,
    Translation,
    Reasoning,
}

#[derive(Debug, Clone)]
pub enum ModelLocation {
    Local,
    Remote,
}

#[derive(Debug, Clone)]
pub struct AIModel {
    pub id: String,
    pub name: String,
    pub version: String,

    pub model_type: ModelType,

    pub provider: String,

    pub location: ModelLocation,

    pub enabled: bool,

    pub priority: u32,
}
