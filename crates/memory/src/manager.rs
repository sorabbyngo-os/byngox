use crate::cache::PromptCache;

pub struct MemoryManager {
    cache: PromptCache,
}

impl MemoryManager {
    pub fn new() -> Self {
        Self {
            cache: PromptCache::new(),
        }
    }

    pub fn store_interaction(&mut self, user: &str, prompt: &str, response: &str) {
        self.cache
            .store(user, prompt, response);
    }

    pub fn recent(&self, user: &str) -> Vec<(String, String)> {
        self.cache.recent(user)
    }
}
