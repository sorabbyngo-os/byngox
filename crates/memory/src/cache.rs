use std::collections::HashMap;

pub struct PromptCache {

    entries: HashMap<String,String>,

}

impl PromptCache {

    pub fn new() -> Self {

        Self {

            entries: HashMap::new(),

        }

    }

}
