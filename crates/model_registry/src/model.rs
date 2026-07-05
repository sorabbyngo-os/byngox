use crate::{Capability, ModelMetadata};

#[derive(Clone, Debug)]
pub struct Model {
    pub id: String,
    pub provider: String,
    pub metadata: ModelMetadata,
    pub capabilities: Vec<Capability>,
}
