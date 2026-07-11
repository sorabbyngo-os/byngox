use agent_planner::ExecutionPlan;

use crate::TaskStatus;

pub struct RunningTask {
    pub plan: ExecutionPlan,
    pub current_step: usize,
    pub status: TaskStatus,
}

impl RunningTask {
    pub fn new(plan: ExecutionPlan) -> Self {
        Self {
            plan,
            current_step: 0,
            status: TaskStatus::Pending,
        }
    }
}
