#[derive(Clone, Debug)]

pub struct ModelSelection {

    pub provider: String,

    pub model: String,

    pub local: bool,

    pub estimated_cost: f32,

    pub latency: u32,

}
