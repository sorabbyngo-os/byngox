use crate::{
    Intent,
    ReasoningStrategy,
};

pub struct StrategySelector;

impl StrategySelector {

    pub fn select(
        intent: &Intent,
    ) -> ReasoningStrategy {

        match intent {

            Intent::Conversation =>
                ReasoningStrategy::DirectAnswer,

            Intent::Question =>
                ReasoningStrategy::DirectAnswer,

            Intent::ToolUse =>
                ReasoningStrategy::ToolExecution,

            Intent::MultiStepTask =>
                ReasoningStrategy::Planning,

            Intent::Unknown =>
                ReasoningStrategy::Reflection,
        }
    }
}
