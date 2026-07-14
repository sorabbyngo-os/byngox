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
        id: "goal-1".to_string(),
        description: prompt.to_string(),
        capabilities: Vec::new(),
    }]
  }
}
