use crate::ModelScore;

#[derive(Clone, Debug)]
pub struct RoutingRequest;

#[derive(Clone, Debug)]
pub struct RoutingResponse {
    pub selected: ModelScore,
}
