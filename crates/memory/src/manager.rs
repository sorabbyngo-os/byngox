use crate::MemoryRetrieval;
use crate::{
    cache::PromptCache,
    store::MemoryStore,
};

pub struct MemoryManager {
    cache: PromptCache,
    store: MemoryStore,

}

impl MemoryManager {
    pub fn new() -> Self {
	Self {
    	  cache: PromptCache::new(),
    	  store: MemoryStore::new(),
        }

    }

    pub fn store_interaction(&mut self, user: &str, prompt: &str, response: &str) {
        self.cache.store(user, prompt, response);
    }

    pub fn recent(&self, user: &str) -> Vec<(String, String)> {
        self.cache.recent(user)
    }
    
    pub fn store_memory(
   	 &mut self,
   	 user: &str,
   	 memory: String,
    ) {
         self.store.store(user, memory);
    }

    pub fn retrieve_memory(
    	&self,
    	user: &str,
    ) -> Vec<String> {
    	self.store.retrieve(user)
    }
    pub fn search_memory(
       &self,
       user: &str,
       query: &str,
    ) -> Vec<String> {

      MemoryRetrieval::search(
        &self.store,
        user,
        query,
      )
    }
}
