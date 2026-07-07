use crate::Message;

pub struct ContextWindow {
    max_messages: usize,
}

impl ContextWindow {
    pub fn new(max_messages: usize) -> Self {
        Self { max_messages }
    }

    pub fn apply(&self, history: &[Message]) -> Vec<Message> {
        history
            .iter()
            .rev()
            .take(self.max_messages)
            .cloned()
            .collect::<Vec<_>>()
            .into_iter()
            .rev()
            .collect()
    }
}
