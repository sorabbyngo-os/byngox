#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct CapabilityMetadata {
    pub description: String,
    pub version: String,

    pub realtime: bool,

    pub offline_supported: bool,

}
