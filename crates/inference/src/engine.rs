use crate::{
    InferenceError,
    InferenceRequest,
    InferenceResponse,
};

pub struct InferenceEngine;

impl InferenceEngine {

    pub fn new() -> Self {
        Self
    }

    pub fn execute(
        &self,
        request: InferenceRequest,
    ) -> Result<InferenceResponse, InferenceError> {

        println!(
            "Executing capability: {}",
            request.capability
        );

        Ok(
            InferenceResponse {

                model: "placeholder".into(),

                output: format!(
                    "Processed: {}",
                    request.prompt
                ),
            }
        )
    }
}
