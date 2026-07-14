use ai_core::Capability;

use crate::{CapabilityDefinition, CapabilityMetadata};

pub fn default_capabilities() -> Vec<CapabilityDefinition> {
    vec![
        CapabilityDefinition {
            capability: Capability::Reasoning,
            id: "reasoning".into(),
            metadata: CapabilityMetadata {
                description: "General reasoning".into(),
                ..Default::default()
            },
        },
        CapabilityDefinition {
            capability: Capability::Coding,
            id: "coding".into(),
            metadata: CapabilityMetadata {
                description: "Code generation and analysis".into(),
                ..Default::default()
            },
        },
        CapabilityDefinition {
            capability: Capability::Vision,
            id: "vision".into(),
            metadata: CapabilityMetadata {
                description: "Image understanding".into(),
                ..Default::default()
            },
        },
        CapabilityDefinition {
            capability: Capability::Audio,
            id: "audio".into(),
            metadata: CapabilityMetadata {
                description: "Audio understanding".into(),
                ..Default::default()
            },
        },
        CapabilityDefinition {
            capability: Capability::SpeechRecognition,
            id: "speech_recognition".into(),
            metadata: CapabilityMetadata {
                description: "Speech recognition".into(),
                ..Default::default()
            },
        },
        CapabilityDefinition {
            capability: Capability::SpeechSynthesis,
            id: "speech_synthesis".into(),
            metadata: CapabilityMetadata {
                description: "Speech synthesis".into(),
                ..Default::default()
            },
        },
        CapabilityDefinition {
            capability: Capability::Translation,
            id: "translation".into(),
            metadata: CapabilityMetadata {
                description: "Language translation".into(),
                ..Default::default()
            },
        },
        CapabilityDefinition {
            capability: Capability::Planning,
            id: "planning".into(),
            metadata: CapabilityMetadata {
                description: "Task planning".into(),
                ..Default::default()
            },
        },
        CapabilityDefinition {
            capability: Capability::Embedding,
            id: "embedding".into(),
            metadata: CapabilityMetadata {
                description: "Vector embeddings".into(),
                ..Default::default()
            },
        },
        CapabilityDefinition {
            capability: Capability::ImageGeneration,
            id: "image_generation".into(),
            metadata: CapabilityMetadata {
                description: "Image generation".into(),
                ..Default::default()
            },
        },
        CapabilityDefinition {
            capability: Capability::VideoUnderstanding,
            id: "video_understanding".into(),
            metadata: CapabilityMetadata {
                description: "Video understanding".into(),
                ..Default::default()
            },
        },
        CapabilityDefinition {
            capability: Capability::VideoGeneration,
            id: "video_generation".into(),
            metadata: CapabilityMetadata {
                description: "Video generation".into(),
                ..Default::default()
            },
        },
        CapabilityDefinition {
            capability: Capability::Robotics,
            id: "robotics".into(),
            metadata: CapabilityMetadata {
                description: "Robotics".into(),
                ..Default::default()
            },
        },
    ]
}
