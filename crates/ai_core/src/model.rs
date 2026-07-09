use crate::Capability;

#[derive(Clone, Debug)]
pub struct ModelMetadata {
    // Identity
    pub family: String,
    pub architecture: Option<String>,
    pub format: Option<String>,

    // Model characteristics
    pub parameter_size: Option<String>,
    pub quantization: Option<String>,

    // Limits
    pub context_window: usize,
    pub max_output_tokens: usize,
    pub embedding_dimension: Option<usize>,

    // Capabilities
    pub supports_completion: bool,
    pub supports_chat: bool,
    pub supports_tools: bool,
    pub supports_embeddings: bool,
    pub supports_streaming: bool,
    pub supports_vision: bool,
    pub supports_audio: bool,
    pub supports_image_generation: bool,
}

#[derive(Clone, Debug)]
pub struct Model {
    /// Unique identifier.
    /// Examples:
    /// - llama3:latest
    /// - phi4-mini:latest
    /// - gpt-4.1
    /// - claude-opus-4
    pub id: String,

    /// Provider name.
    /// Examples:
    /// ollama
    /// openai
    /// anthropic
    /// gemini
    /// llama_cpp
    /// vllm
    pub provider: String,

    pub metadata: ModelMetadata,

    /// Generic capabilities understood by ByngoX.
    pub capabilities: Vec<Capability>,
}
