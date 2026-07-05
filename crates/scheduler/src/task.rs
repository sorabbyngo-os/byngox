use std::time::SystemTime;

#[derive(Debug, Clone)]
pub enum TaskState {
    Pending,
    Running,
    Completed,
    Failed,
    Suspended,
}

#[derive(Debug, Clone)]
pub struct Task {
    pub id: u64,
    pub name: String,
    pub created: SystemTime,
    pub priority: crate::Priority,
    pub state: TaskState,
}
