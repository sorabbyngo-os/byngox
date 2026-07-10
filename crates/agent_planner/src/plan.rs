use crate::PlanStep;

#[derive(Debug, Clone)]
pub struct ExecutionPlan {
    pub steps: Vec<PlanStep>,
}

impl ExecutionPlan {
    pub fn new() -> Self {
        Self {
            steps: Vec::new(),
        }
    }

    pub fn add_step(
        &mut self,
        step: PlanStep,
    ) {
        self.steps.push(step);
    }

    pub fn is_empty(&self) -> bool {
        self.steps.is_empty()
    }
}
