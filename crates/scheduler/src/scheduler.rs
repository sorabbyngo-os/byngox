use crate::{queue::TaskQueue, Task};

pub struct Scheduler {
    queue: TaskQueue,
}

impl Scheduler {
    pub fn new() -> Self {
        Self {
            queue: TaskQueue::new(),
        }
    }

    pub fn submit(&mut self, task: Task) {
        self.queue.push(task);
    }

    pub fn next_task(&mut self) -> Option<Task> {
        self.queue.pop()
    }

    pub fn pending_tasks(&self) -> usize {
        self.queue.len()
    }
}
