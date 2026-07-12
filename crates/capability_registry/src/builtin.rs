pub fn register_builtin(registry: &mut ProviderRegistry) {
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
        id: "reasoning".into(),
        capability: ToolCapability::Reasoning,
        target: "reasoning".into(),
        priority: 100,
    });
}
