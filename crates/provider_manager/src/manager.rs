use ai_core::Model;

use crate::Provider;

pub struct ProviderManager {
    providers: Vec<Box<dyn Provider>>,
}

impl ProviderManager {
    pub fn new() -> Self {
        Self {
            providers: Vec::new(),
        }
    }

    pub fn register(&mut self, provider: Box<dyn Provider>) {
        self.providers.push(provider);
    }

    pub fn discover_models(&self) -> Result<Vec<Model>, Box<dyn std::error::Error>> {
        println!("Providers registered: {}", self.providers.len());

        let mut models = Vec::new();

        for (i, provider) in self.providers.iter().enumerate() {
            println!("Querying provider {}", i);

            let discovered = provider.discover_models()?;

            println!("Provider returned {} models", discovered.len());

            models.extend(discovered);
        }

        println!("Total discovered models: {}", models.len());

        Ok(models)
    }

    pub fn providers(&self) -> &[Box<dyn Provider>] {
        &self.providers
    }
}
