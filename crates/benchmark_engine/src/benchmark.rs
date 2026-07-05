use crate::ModelMetrics;

#[derive(Clone, Debug)]

pub struct BenchmarkRecord {

    pub provider: String,

    pub model: String,

    pub capability: String,

    pub metrics: ModelMetrics,

}
