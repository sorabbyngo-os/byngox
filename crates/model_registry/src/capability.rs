#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Capability {
    Chat,
    Coding,
    SpeechRecognition,
    SpeechSynthesis,
    Vision,
    OCR,
    Translation,
    Planning,
    MedicalReasoning,
    ImageGeneration,
    VideoUnderstanding,
}
