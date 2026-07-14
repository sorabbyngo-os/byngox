#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct CapabilityMetadata {
    pub description: String,
    pub version: String,
    pub realtime: bool,
    pub offline_supported: bool,
}

impl Default for CapabilityMetadata {
    fn default() -> Self {
        Self {
            description: String::new(),
            version: "1.0.0".into(),
            realtime: false,
            offline_supported: true,
        }
    }
}
