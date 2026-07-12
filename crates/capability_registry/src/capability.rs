use tool_capability::ToolCapability;

#[derive(Clone, Debug)]
pub struct CapabilityDefinition {
    pub capability: ToolCapability,

    pub id: String,

    pub metadata: crate::CapabilityMetadata,
}
