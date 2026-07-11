use std::collections::VecDeque;

use agent_planner::ExecutionPlan;

pub struct TaskQueue {
    queue: VecDeque<ExecutionPlan>,
}

impl TaskQueue {
    pub fn new() -> Self {
        Self {
            queue: VecDeque::new(),
        }
    }

    pub fn push(&mut self, plan: ExecutionPlan) {
        self.queue.push_back(plan);
    }

    pub fn pop(&mut self) -> Option<ExecutionPlan> {
        self.queue.pop_front()
    }

    pub fn is_empty(&self) -> bool {
        self.queue.is_empty()
    }

    pub fn len(&self) -> usize {
        self.queue.len()
    }
}
