use context::Message;

use crate::{conversation::ConversationFormatter, system::SystemPrompt};

pub struct PromptBuilder;

impl PromptBuilder {
    pub fn new() -> Self {
        Self
    }

    pub fn build(&self, messages: &[Message]) -> String {
        let mut prompt = String::new();

        prompt.push_str(&SystemPrompt::default());
        prompt.push_str("\n\n");

        prompt.push_str(&ConversationFormatter::format(messages));

        prompt
    }
}
