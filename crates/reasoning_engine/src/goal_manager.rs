use crate::Goal;
//#[derive(Debug, Clone)]
//pub struct Goal {
//    pub description: String,
//}

pub struct GoalManager;

impl GoalManager {
    pub fn new() -> Self {
        Self
    }

    pub fn extract(&self, prompt: &str) -> Vec<Goal> {
        vec![Goal {
            description: prompt.to_string(),
        }]
    }
}
