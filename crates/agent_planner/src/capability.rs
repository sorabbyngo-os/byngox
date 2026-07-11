#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Capability {
    Filesystem,
    Web,
    Shell,
    Memory,
    Reasoning,
}
