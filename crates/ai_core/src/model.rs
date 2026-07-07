use crate::Capability;

#[derive(Clone, Debug)]
pub struct ModelMetadata {
    pub family: String,
    pub context_window: usize,
    pub max_output_tokens: usize,
}

#[derive(Clone, Debug)]
pub struct Model {
    pub id: String,
    pub provider: String,
    pub metadata: ModelMetadata,
    pub capabilities: Vec<Capability>,
}
