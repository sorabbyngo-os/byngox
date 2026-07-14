pub fn register_builtin(registry: &mut ProviderRegistry) {
    registry.register(CapabilityProvider {
        id: "filesystem".into(),
        capability: capability::Filesystem,
        target: "filesystem".into(),
        priority: 100,
    });

    registry.register(CapabilityProvider {
        id: "web".into(),
        capability: capability::Web,
        target: "web".into(),
        priority: 100,
    });

    registry.register(CapabilityProvider {
        id: "shell".into(),
        capability: capability::Shell,
        target: "shell".into(),
        priority: 100,
    });

    registry.register(CapabilityProvider {
        id: "reasoning".into(),
        capability: capability::Reasoning,
        target: "reasoning".into(),
        priority: 100,
    });
}
