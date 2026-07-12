#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ToolCapability {
    Filesystem,
    Web,
    Shell,
    Memory,
    Reasoning,
}
