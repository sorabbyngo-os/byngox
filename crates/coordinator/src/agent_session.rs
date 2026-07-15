use execution_engine::HistoryStore;

pub struct AgentSession {
    history: HistoryStore,
}

impl AgentSession {
    pub fn new() -> Self {
        Self {
            history: HistoryStore::new(),
        }
    }

    pub fn history(&self) -> &HistoryStore {
        &self.history
    }
}

impl Default for AgentSession {
    fn default() -> Self {
        Self::new()
    }
}
