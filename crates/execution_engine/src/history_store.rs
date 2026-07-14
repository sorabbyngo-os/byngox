use std::sync::{Arc, Mutex};

use crate::ExecutionRecord;

#[derive(Clone)]
pub struct HistoryStore {
    records: Arc<Mutex<Vec<ExecutionRecord>>>,
}

impl HistoryStore {
    pub fn new() -> Self {
        Self {
            records: Arc::new(Mutex::new(Vec::new())),
        }
    }

    pub fn push(&self, record: ExecutionRecord) {
        self.records.lock().unwrap().push(record);
    }

    pub fn all(&self) -> Vec<ExecutionRecord> {
        self.records.lock().unwrap().clone()
    }
}

impl Default for HistoryStore {
    fn default() -> Self {
        Self::new()
    }
}
