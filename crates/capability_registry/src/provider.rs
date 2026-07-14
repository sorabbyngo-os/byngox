use ai_core::Capability;

#[derive(Debug, Clone)]
pub struct CapabilityProvider {
    pub id: String,
    pub capability: Capability,
    pub target: String,
    pub priority: u32,
}
