pub trait BackendRuntime {
    fn id(&self) -> &str;

    fn initialize(&mut self) -> Result<(), String>;

    fn shutdown(&mut self) -> Result<(), String>;

    fn health(&self) -> bool;
}

pub trait ProviderBackend {
    fn id(&self) -> &str;

    fn backend(&self) -> &str;
}

pub trait Planner {
    fn plan(&self, goal: &str) -> Vec<String>;
}

pub trait Reasoner {
    fn reason(&self, input: &str) -> Result<String, String>;
}
