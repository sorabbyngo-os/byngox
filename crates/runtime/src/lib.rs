use std::collections::HashMap;

pub trait Engine: Send + Sync {
    fn name(&self) -> &'static str;

    fn initialize(&mut self) -> Result<(), String>;

    fn start(&mut self) -> Result<(), String>;

    fn shutdown(&mut self) -> Result<(), String>;
}

pub struct Runtime {
    engines: HashMap<String, Box<dyn Engine>>,
}

impl Runtime {
    pub fn new() -> Self {
        Self {
            engines: HashMap::new(),
        }
    }

    pub fn register<E: Engine + 'static>(&mut self, engine: E) {
        self.engines
            .insert(engine.name().to_string(), Box::new(engine));
    }

    pub fn initialize(&mut self) {
        for engine in self.engines.values_mut() {
            let _ = engine.initialize();
        }
    }

    pub fn start(&mut self) {
        for engine in self.engines.values_mut() {
            let _ = engine.start();
        }
    }

    pub fn shutdown(&mut self) {
        for engine in self.engines.values_mut() {
            let _ = engine.shutdown();
        }
    }

    pub fn engine_count(&self) -> usize {
        self.engines.len()
    }
}
