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

}
