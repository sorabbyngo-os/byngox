#[derive(Debug, Clone, PartialEq, Eq)]
pub enum AgentAction {
    Respond,
    UseTool,
    Finish,
}
