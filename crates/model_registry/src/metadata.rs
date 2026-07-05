#[derive(Clone, Debug)]
pub struct ModelMetadata {
    pub name: String,
    pub version: String,

    pub parameters: u64,

    pub context_window: usize,

    pub quantization: String,

    pub local_only: bool,
}
