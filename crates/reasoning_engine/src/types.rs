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
    pub description: String,
}

#[derive(Debug, Clone)]
pub struct ReasoningResult {
    pub intent: Intent,
    pub strategy: ReasoningStrategy,
    pub goals: Vec<Goal>,
}
