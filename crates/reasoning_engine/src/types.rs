#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Intent {
    Conversation,
    Question,
    ToolUse,
    MultiStepTask,
    Unknown,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ReasoningStrategy {
    DirectAnswer,
    ToolExecution,
    Planning,
    Reflection,
}

#[derive(Debug, Clone)]
pub struct Goal {
    pub id: String,

    pub description: String,

    pub capabilities: Vec<ai_core::Capability>,
}

#[derive(Debug, Clone)]
pub struct ReasoningResult {
    pub intent: Intent,
    pub strategy: ReasoningStrategy,
    pub goals: Vec<Goal>,
}
