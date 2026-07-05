use std::sync::{Arc, RwLock};

#[derive(Debug, Clone)]
pub enum Event {
    SystemStarted,
    SystemShutdown,

    CapabilityRegistered(String),

    CapabilityRemoved(String),

    ModelInstalled(String),

    ModelRemoved(String),

    InferenceRequested(String),

    InferenceCompleted(String),

    MemoryPressure,

    PowerChanged,

    WakeWordDetected,

    SecurityAlert(String),
}

pub trait EventListener: Send + Sync {
    fn on_event(&self, event: &Event);
}

pub struct EventBus {
    listeners: Arc<RwLock<Vec<Box<dyn EventListener>>>>,
}

impl EventBus {
    pub fn new() -> Self {
        Self {
            listeners: Arc::new(RwLock::new(Vec::new())),
        }
    }

    pub fn subscribe<L>(&self, listener: L)
    where
        L: EventListener + 'static,
    {
        self.listeners.write().unwrap().push(Box::new(listener));
    }

    pub fn publish(&self, event: Event) {
        let listeners = self.listeners.read().unwrap();

        for listener in listeners.iter() {
            listener.on_event(&event);
        }
    }
}
