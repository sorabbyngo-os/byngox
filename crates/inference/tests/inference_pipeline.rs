use ai_core::Capability;
use inference::{InferenceEngine, InferenceRequest};

#[test]
fn inference_pipeline_executes() {
    let mut engine = InferenceEngine::new();

    let request = InferenceRequest {
        capability: Capability::Reasoning,
        prompt: "Say hello from ByngoX".to_string(),
        user_id: "integration-test".to_string(),
    };

    match engine.execute(request) {
        Ok(response) => {
            println!("MODEL  : {}", response.model);
            println!("OUTPUT : {}", response.output);

            assert!(!response.output.is_empty());
        }

        Err(err) => {
            panic!("Inference failed: {:?}", err);
        }
    }
}
