use std::time::SystemTime;
pub mod bus;
pub type EngineId = String;
pub type EventType = String;

#[derive(Debug, Clone)]
pub struct Event {
    pub id: u64,
    pub event_type: EventType,
    pub source: EngineId,
    pub target: Option<EngineId>,
    pub timestamp: SystemTime,
    pub payload: EventPayload,
}

#[derive(Debug, Clone)]
pub enum EventPayload {
    None,

    Text(String),

    Binary(Vec<u8>),

    AudioFrame(Vec<i16>),

    ImageFrame(Vec<u8>),

    ModelRequest(ModelRequest),

    ModelResponse(ModelResponse),

    CapabilityRequest(String),

    CapabilityResponse(String),

    Shutdown,

    Heartbeat,
}

#[derive(Debug, Clone)]
pub struct ModelRequest {
    pub task: String,
    pub input: String,
}

#[derive(Debug, Clone)]
pub struct ModelResponse {
    pub model: String,
    pub output: String,
}
