use model_registry::Model;

#[derive(Clone, Debug)]
pub struct ModelScore {
    pub model: Model,
    pub score: f32,
}
