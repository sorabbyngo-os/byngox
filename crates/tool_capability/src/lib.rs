#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum ToolCapability {
    Filesystem,
    Web,
    Shell,
    Memory,
    Reasoning,
}
