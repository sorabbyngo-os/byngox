use benchmark_engine::ModelScore;

pub struct RoutingRequest;

pub struct RoutingResponse {

    pub model: ModelScore,

}

pub struct ModelRouter;

impl ModelRouter {

    pub fn new() -> Self {
        Self
    }

   pub fn select(
    &self,
    candidates: Vec<ModelScore>,
   ) -> Option<RoutingResponse> {

       candidates.first().map(|candidate| RoutingResponse {

           model: candidate.clone(),

       })

    }

}

impl RoutingResponse {

  pub fn name(&self) -> &str {
    &self.model.model.id
  }

}
