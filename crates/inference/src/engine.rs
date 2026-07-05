use uuid::Uuid;

use crate::{
    InferenceError,
    InferenceRequest,
    InferenceResponse,
    InferenceSession,
};

pub struct InferenceEngine;

impl InferenceEngine {

    pub fn new() -> Self {

        Self

    }

    pub fn create_session(

        &self,

    ) -> InferenceSession {

        InferenceSession {

            id: Uuid::new_v4(),

        }

    }

    pub fn infer(

        &self,

        _session: &InferenceSession,

        request: InferenceRequest,

    ) -> Result<InferenceResponse,InferenceError> {

        Ok(

            InferenceResponse {

                output: format!(

                    "Inference executed using {}",

                    request.model,

                ),

            }

        )

    }

}
