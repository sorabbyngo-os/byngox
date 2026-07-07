#[derive(Clone, Debug)]

pub struct RuntimeContext {
    pub active_model: Option<String>,

    pub active_provider: Option<String>,
}
