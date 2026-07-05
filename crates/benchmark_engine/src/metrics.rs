#[derive(Clone, Debug)]

pub struct ModelMetrics {

    pub latency_ms: u32,

    pub ram_mb: u32,

    pub vram_mb: u32,

    pub power_watts: f32,

    pub accuracy: f32,

    pub trust_score: f32,

}
