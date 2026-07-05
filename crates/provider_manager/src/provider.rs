pub struct ProviderInfo {
    pub id: String,
    pub vendor: String,
    pub local: bool,
}

pub trait ModelProvider: Send + Sync {

    fn info(&self) -> ProviderInfo;

    fn load(&mut self) -> Result<(), String>;

    fn unload(&mut self) -> Result<(), String>;

    fn infer(
        &self,
        prompt: &str,
    ) -> Result<String,String>;
}
