use crate::{
    RoutingDecision,
    RoutingRequest,
};

pub struct ModelRouter;

impl ModelRouter {

    pub fn new() -> Self {

        Self

    }

    pub fn route(

        &self,

        request: RoutingRequest,

    ) -> RoutingDecision {

        RoutingDecision {

            provider: "local".into(),

            model: format!("default-{}", request.capability),

        }

    }

}
