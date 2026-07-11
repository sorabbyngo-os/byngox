use crate::Goal;

#[derive(Debug, Clone)]
pub struct ReasoningPlan {
    pub goals: Vec<Goal>,
}

pub struct ReasoningPlanner;

impl ReasoningPlanner {

    pub fn new() -> Self {
        Self
    }

    pub fn create_plan(
        &self,
        goals: Vec<Goal>,
    ) -> ReasoningPlan {

        ReasoningPlan {
            goals,
        }
    }
}
