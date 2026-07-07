use ai_core::ModelSelection;
#[derive(Clone, Debug)]
pub struct ExecutionPlan {
    pub selection: ModelSelection,

    pub capability: String,

    pub requires_memory: bool,

    pub requires_context: bool,
}
