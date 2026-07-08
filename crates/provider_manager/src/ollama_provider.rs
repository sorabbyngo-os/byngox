use std::error::Error;

use crate::Provider;

pub struct OllamaProvider;

impl OllamaProvider {

    pub fn new() -> Self {
        Self
    }

}

impl Provider for OllamaProvider {

    fn generate(
        &self,
        _prompt: &str,
    ) -> Result<String, Box<dyn Error>> {

        Ok(String::from(
            "Ollama stub response",
        ))

    }

}
