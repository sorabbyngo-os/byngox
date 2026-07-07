use std::collections::HashMap;

pub struct PromptCache {
    entries: HashMap<String, Vec<(String, String)>>,
}

impl PromptCache {
    pub fn new() -> Self {
        Self {
            entries: HashMap::new(),
        }
    }

    pub fn store(
        &mut self,
        user: &str,
        prompt: &str,
        response: &str,
    ) {
        self.entries
            .entry(user.to_string())
            .or_default()
            .push((prompt.to_string(), response.to_string()));
    }

    pub fn recent(
        &self,
        user: &str,
    ) -> Vec<(String, String)> {
        self.entries
            .get(user)
            .cloned()
            .unwrap_or_default()
    }
}
