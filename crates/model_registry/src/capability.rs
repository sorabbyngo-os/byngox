#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum Capability {
    Reasoning,
    Coding,
    Vision,
    Audio,
    SpeechRecognition,
    SpeechSynthesis,
    Translation,
    Planning,
    Embedding,
    ImageGeneration,
    VideoUnderstanding,
    VideoGeneration,
    Robotics,
}
