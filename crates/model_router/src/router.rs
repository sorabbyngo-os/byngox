use crate::{
    CandidateModel,
    RoutingRequest,
    RoutingResponse,
};

pub struct ModelRouter;

impl ModelRouter {

    pub fn new() -> Self {

        Self

    }

    pub fn select(

        &self,

        _request: RoutingRequest,

        mut candidates: Vec<CandidateModel>,

    ) -> Option<RoutingResponse> {

        candidates.sort_by(|a, b| {

            b.benchmark_score
                .partial_cmp(&a.benchmark_score)
                .unwrap()

        });

        let best = candidates.first()?;

        Some(

            RoutingResponse {

                selected_model: best.name.clone(),

            }

        )

    }

}
