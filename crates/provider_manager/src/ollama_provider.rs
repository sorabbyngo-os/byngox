use std::error::Error;

use reqwest::blocking::Client;

use ai_core::{Capability, Model, ModelMetadata};

use crate::{OllamaRequest, OllamaResponse, OllamaTagsResponse, Provider};

pub struct OllamaProvider {
    client: Client,
}

impl OllamaProvider {
    pub fn new() -> Self {
        Self {
            client: Client::new(),
        }
    }
}

impl Provider for OllamaProvider {
    fn discover_models(&self) -> Result<Vec<Model>, Box<dyn Error>> {
        let tags: OllamaTagsResponse = self
            .client
            .get("http://localhost:11434/api/tags")
            .send()?
            .json()?;

        let mut models = Vec::new();

        for model in tags.models {
            models.push(Model {
                id: model.name.clone(),
                provider: "ollama".to_string(),

                metadata: ModelMetadata {
                    family: model
                        .details
                        .family
                        .clone()
                        .unwrap_or_else(|| "unknown".into()),

                    architecture: model.details.families.first().cloned(),

                    format: model.details.format.clone(),

                    parameter_size: model.details.parameter_size.clone(),

                    quantization: model.details.quantization_level.clone(),

                    context_window: model.details.context_length.unwrap_or(4096),

                    max_output_tokens: model.details.context_length.unwrap_or(4096),

                    embedding_dimension: model.details.embedding_length,

                    supports_completion: true,

                    supports_chat: true,

                    supports_tools: model.capabilities.iter().any(|c| c == "tools"),

                    supports_embeddings: model.capabilities.iter().any(|c| c == "embedding"),

                    supports_streaming: true,

                    supports_vision: model.capabilities.iter().any(|c| c == "vision"),

                    supports_audio: model.capabilities.iter().any(|c| c == "audio"),

                    supports_image_generation: model.capabilities.iter().any(|c| c == "image"),
                },

                capabilities: vec![
                    Capability::Reasoning,
                    Capability::Coding,
                    Capability::Planning,
                    Capability::Translation,
                ],
            });
        }

        Ok(models)
    }

    fn generate(&self, model: &Model, prompt: &str) -> Result<String, Box<dyn Error>> {
        let request = OllamaRequest {
            model: model.id.clone(),
            prompt: prompt.to_string(),
            stream: false,
        };

        let response = self
            .client
            .post("http://localhost:11434/api/generate")
            .json(&request)
            .send()?;

        let body: OllamaResponse = response.json()?;

        Ok(body.response)
    }
}
