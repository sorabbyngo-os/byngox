use crate::{
    RunningTask,
    TaskStatus,
};

pub struct ExecutionState {
    pub task: RunningTask,
}

impl ExecutionState {
    pub fn new(task: RunningTask) -> Self {
        Self { task }
    }

    pub fn current_step(&self) -> usize {
        self.task.current_step
    }

    pub fn advance(&mut self) {
        self.task.current_step += 1;
    }

    pub fn status(&self) -> TaskStatus {
        self.task.status
    }

    pub fn set_status(
        &mut self,
        status: TaskStatus,
    ) {
        self.task.status = status;
    }

    pub fn finished(&self) -> bool {
        self.task.current_step >= self.task.plan.steps.len()
    }
}
