use crate::Model;

#[derive(Clone, Debug)]
pub struct BenchmarkMetrics {
    pub accuracy: f32,
    pub latency_ms: f32,
    pub throughput: f32,
    pub memory_mb: f32,
    pub energy_watts: f32,
}

impl Default for BenchmarkMetrics {
    fn default() -> Self {
        Self {
            accuracy: 0.0,
            latency_ms: 0.0,
            throughput: 0.0,
            memory_mb: 0.0,
            energy_watts: 0.0,
        }
    }
}

#[derive(Clone, Debug)]
pub struct ModelScore {
    pub model: Model,
    pub score: f32,
    pub metrics: BenchmarkMetrics,
}

#[derive(Clone, Debug)]
pub struct BenchmarkRecord {
    pub model: Model,
    pub metrics: BenchmarkMetrics,
}
