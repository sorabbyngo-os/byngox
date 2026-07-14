use crate::{AgentAction, ExecutionPlan, PlanStep};

pub struct PlanBuilder {
    plan: ExecutionPlan,
    counter: usize,
}

impl PlanBuilder {
    pub fn new() -> Self {
        Self {
            plan: ExecutionPlan::new(),
            counter: 0,
        }
    }

    fn next_id(&mut self) -> String {
        self.counter += 1;
        format!("step-{}", self.counter)
    }

    pub fn add_step(
        &mut self,
        runtime: impl Into<String>,
        action: AgentAction,
        target: impl Into<String>,
        input: impl Into<String>,
    ) -> String {
        let id = self.next_id();

        self.plan
            .add_step(PlanStep::new(id.clone(), runtime, action, target, input));

        id
    }

    pub fn add_step_after(
        &mut self,
        dependency: &str,
        runtime: impl Into<String>,
        action: AgentAction,
        target: impl Into<String>,
        input: impl Into<String>,
    ) -> String {
        let id = self.next_id();

        self.plan.add_step(
            PlanStep::new(id.clone(), runtime, action, target, input).depends_on(dependency),
        );

        id
    }

    pub fn build(self) -> ExecutionPlan {
        self.plan
    }
}

impl Default for PlanBuilder {
    fn default() -> Self {
        Self::new()
    }
}
