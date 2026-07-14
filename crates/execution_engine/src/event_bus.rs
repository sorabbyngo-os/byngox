use std::sync::{Arc, Mutex};

use crate::ExecutionEvent;

#[derive(Clone)]
pub struct EventBus {
    events: Arc<Mutex<Vec<ExecutionEvent>>>,
}

impl EventBus {
    pub fn new() -> Self {
        Self {
            events: Arc::new(Mutex::new(Vec::new())),
        }
    }

    pub fn publish(&self, event: ExecutionEvent) {
        self.events.lock().unwrap().push(event);
    }

    pub fn events(&self) -> Vec<ExecutionEvent> {
        self.events.lock().unwrap().clone()
    }
}

impl Default for EventBus {
    fn default() -> Self {
        Self::new()
    }
}
