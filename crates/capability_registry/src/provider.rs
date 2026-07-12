use tool_capability::ToolCapability;

#[derive(Debug, Clone)]
pub struct CapabilityProvider {
    pub id: String,
    pub capability: ToolCapability,
    pub target: String,
    pub priority: u32,
}
