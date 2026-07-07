use crate::{ContextState, ContextWindow, ConversationHistory, Message};

pub struct ContextManager {
    history: ConversationHistory,
    window: ContextWindow,
    state: ContextState,
}

impl ContextManager {
    pub fn new() -> Self {
        Self {
            history: ConversationHistory::new(),
            window: ContextWindow::new(32),
            state: ContextState {
                user_id: String::new(),
                session_id: String::new(),
            },
        }
    }

    pub fn add(&mut self, message: Message) {
        self.history.push(message);
    }

    pub fn window(&self) -> Vec<Message> {
        self.window.apply(self.history.messages())
    }

    pub fn state(&self) -> &ContextState {
        &self.state
    }
}
