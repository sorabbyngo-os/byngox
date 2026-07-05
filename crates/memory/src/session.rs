use uuid::Uuid;

#[derive(Clone, Debug)]
pub struct InferenceSessionMemory {

    pub session: Uuid,

    pub prompt_history: Vec<String>,

    pub response_history: Vec<String>,

}
