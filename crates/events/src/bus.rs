use std::sync::{Arc, Mutex};

use crate::Event;

pub type Subscriber = Arc<dyn Fn(Event) + Send + Sync>;

pub struct EventBus {
    subscribers: Mutex<Vec<Subscriber>>,
}

impl EventBus {
    pub fn new() -> Self {
        Self {
            subscribers: Mutex::new(Vec::new()),
        }
    }

    pub fn subscribe(&self, callback: Subscriber) {
        self.subscribers.lock().unwrap().push(callback);
    }

    pub fn publish(&self, event: Event) {
        let subscribers = self.subscribers.lock().unwrap();

        for subscriber in subscribers.iter() {
            subscriber(event.clone());
        }
    }
}
