use crate::{
    Intent,
};

pub struct IntentAnalyzer;

impl IntentAnalyzer {

    pub fn new() -> Self {
        Self
    }

    pub fn analyze(
        &self,
        prompt: &str,
    ) -> Intent {

        let prompt = prompt.trim().to_lowercase();

        if prompt.starts_with("shell:")
            || prompt.starts_with("read:")
            || prompt.starts_with("web:")
        {
            return Intent::ToolUse;
        }

        if prompt.contains("find")
            || prompt.contains("build")
            || prompt.contains("generate")
            || prompt.contains("analyze")
            || prompt.contains("create")
            || prompt.contains("write")
        {
            return Intent::MultiStepTask;
        }

        if prompt.ends_with('?')
            || prompt.starts_with("what")
            || prompt.starts_with("why")
            || prompt.starts_with("how")
            || prompt.starts_with("when")
            || prompt.starts_with("where")
        {
            return Intent::Question;
        }

        Intent::Conversation
    }
}
