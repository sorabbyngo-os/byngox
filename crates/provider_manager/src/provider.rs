use std::error::Error;

use ai_core::Model;

pub trait Provider: Send + Sync {
    fn discover_models(&self) -> Result<Vec<Model>, Box<dyn Error>>;

    fn generate(&self, model: &Model, prompt: &str) -> Result<String, Box<dyn Error>>;
}
