use ai_core::ModelSelection;
use benchmark_engine::ModelScore;

pub struct RoutingResponse {
    pub selection: ModelSelection,
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

        candidates.first().map(|candidate| {

            RoutingResponse {

                selection: ModelSelection {

                    provider: candidate.model.provider.clone(),

                    model: candidate.model.id.clone(),

                    local: true,

                    estimated_cost: 0.0,

                    latency: 0,

                }

            }

        })

    }
}

impl RoutingResponse {
    pub fn name(&self) -> &str {
        &self.selection.model
    }
}
