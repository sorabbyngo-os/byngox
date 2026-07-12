use tool_capability::ToolCapability;

use crate::{CapabilityProvider, ProviderRegistry};

pub fn load_default_providers(registry: &mut ProviderRegistry) {
    registry.register(CapabilityProvider {
        id: "filesystem".into(),
        capability: ToolCapability::Filesystem,
        target: "filesystem".into(),
        priority: 100,
    });

    registry.register(CapabilityProvider {
        id: "web".into(),
        capability: ToolCapability::Web,
        target: "web".into(),
        priority: 100,
    });

    registry.register(CapabilityProvider {
        id: "shell".into(),
        capability: ToolCapability::Shell,
        target: "shell".into(),
        priority: 100,
    });

    registry.register(CapabilityProvider {
        id: "memory".into(),
        capability: ToolCapability::Memory,
        target: "memory".into(),
        priority: 100,
    });

    registry.register(CapabilityProvider {
        id: "reasoning".into(),
        capability: ToolCapability::Reasoning,
        target: "reasoning".into(),
        priority: 100,
    });
}
