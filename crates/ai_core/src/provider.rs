#[derive(Clone, Debug)]
pub enum ProviderType {
    Ollama,
    LlamaCpp,
    Vllm,
    Onnx,
    OpenAI,
    Anthropic,
    Gemini,
    Custom(String),
}

#[derive(Clone, Debug)]
pub struct Provider {
    pub id: String,
    pub backend: ProviderType,
}
