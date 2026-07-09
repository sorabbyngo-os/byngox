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
