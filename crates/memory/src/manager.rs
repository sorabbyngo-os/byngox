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

pub fn store_interaction(
    &mut self,
    user: &str,
    prompt: &str,
    response: &str,
    ) {

    println!(
        "[memory] {} -> {}",
        user,
        prompt
    );

    println!(
        "[response] {}",
        response
    );

    }
}
