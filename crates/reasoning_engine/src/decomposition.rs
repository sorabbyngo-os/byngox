use crate::Goal;

pub struct TaskDecomposer;

impl TaskDecomposer {
    pub fn new() -> Self {
        Self
    }

    pub fn decompose(&self, prompt: &str) -> Vec<Goal> {
        let mut goals = Vec::new();

        for (index, part) in prompt.split(" and ").enumerate() {
            let goal = part.trim();

            if !goal.is_empty() {
                goals.push(Goal {
                    id: format!("goal-{}", index + 1),
                    description: goal.to_string(),
                    capabilities: Vec::new(),
                });
            }
        }

        if goals.is_empty() {
            goals.push(Goal {
                id: "goal-1".to_string(),
                description: prompt.to_string(),
                capabilities: Vec::new(),
            });
        }

        goals
    }
}
