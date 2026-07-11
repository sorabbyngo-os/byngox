use crate::Capability;

pub struct CapabilityResolver;

impl CapabilityResolver {
    pub fn resolve(capability: Capability) -> &'static str {
        match capability {
            Capability::Filesystem => "filesystem",
            Capability::Web => "web",
            Capability::Shell => "shell",
            Capability::Memory => "memory",
            Capability::Reasoning => "reasoning",
        }
    }
}
