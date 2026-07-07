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

impl Capability {
    pub fn from_str(value: &str) -> Option<Self> {
        match value.to_ascii_lowercase().as_str() {
            "reasoning" => Some(Self::Reasoning),
            "coding" => Some(Self::Coding),
            "vision" => Some(Self::Vision),
            "audio" => Some(Self::Audio),
            "speechrecognition" | "speech_recognition" | "speech-recognition" => {
                Some(Self::SpeechRecognition)
            }
            "speechsynthesis" | "speech_synthesis" | "speech-synthesis" => {
                Some(Self::SpeechSynthesis)
            }
            "translation" => Some(Self::Translation),
            "planning" => Some(Self::Planning),
            "embedding" => Some(Self::Embedding),
            "imagegeneration" | "image_generation" | "image-generation" => {
                Some(Self::ImageGeneration)
            }
            "videounderstanding" | "video_understanding" | "video-understanding" => {
                Some(Self::VideoUnderstanding)
            }
            "videogeneration" | "video_generation" | "video-generation" => {
                Some(Self::VideoGeneration)
            }
            "robotics" => Some(Self::Robotics),
            _ => None,
        }
    }

    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Reasoning => "reasoning",
            Self::Coding => "coding",
            Self::Vision => "vision",
            Self::Audio => "audio",
            Self::SpeechRecognition => "speech_recognition",
            Self::SpeechSynthesis => "speech_synthesis",
            Self::Translation => "translation",
            Self::Planning => "planning",
            Self::Embedding => "embedding",
            Self::ImageGeneration => "image_generation",
            Self::VideoUnderstanding => "video_understanding",
            Self::VideoGeneration => "video_generation",
            Self::Robotics => "robotics",
        }
    }
}
