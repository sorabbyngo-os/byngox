use std::error::Error;

use reqwest::blocking::Client;

use crate::{
    OllamaRequest,
    OllamaResponse,
    Provider,
};

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

    fn generate(
        &self,
        prompt: &str,
    ) -> Result<String, Box<dyn Error>> {

        let request = OllamaRequest {

            model: "llama3".to_string(),

            prompt: prompt.to_string(),

            stream: false,

        };

        let response = self
            .client
            .post("http://localhost:11434/api/generate")
            .json(&request)
            .send()?;

        let body: OllamaResponse =
            response.json()?;

        Ok(body.response)

    }

}
