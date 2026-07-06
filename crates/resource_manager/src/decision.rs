use crate::ExecutionPolicy;

#[derive(Clone, Debug)]

pub struct ExecutionDecision {

    pub allow_execution: bool,

    pub policy: ExecutionPolicy,

}
