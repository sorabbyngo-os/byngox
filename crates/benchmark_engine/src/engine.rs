use model_registry::Model;
use crate::ModelScore;

pub struct BenchmarkEngine;

impl BenchmarkEngine {
    pub fn new() -> Self {
        Self
    }

    pub fn rank(
        &self,
        models: Vec<Model>,
    ) -> Vec<ModelScore> {
        models
            .into_iter()
            .map(|model| ModelScore {
                model,
                score: 100.0,
            })
            .collect()
    }
}
