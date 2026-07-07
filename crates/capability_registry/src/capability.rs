use ai_core::Capability;

#[derive(Clone, Debug)]
pub struct CapabilityDefinition {
    pub capability: Capability,

    pub id: String,

    pub metadata: crate::CapabilityMetadata,
}
