use agent_planner::ExecutionPlan;

use crate::DependencyResolver;

pub struct TaskScheduler {
    resolver: DependencyResolver,
}

impl TaskScheduler {

    pub fn new() -> Self {

        Self {
            resolver: DependencyResolver::new(),
        }
    }

    pub fn schedule(
        &self,
        plan: ExecutionPlan,
    ) -> ExecutionPlan {

        let plan = self.resolver.resolve(plan);

        plan
    }
}
