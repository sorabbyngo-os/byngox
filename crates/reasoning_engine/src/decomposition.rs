use crate::Goal;

pub struct TaskDecomposer;

impl TaskDecomposer {
    pub fn new() -> Self {
        Self
    }

    pub fn decompose(&self, prompt: &str) -> Vec<Goal> {
        let mut goals = Vec::new();

        for part in prompt.split(" and ") {
            let goal = part.trim();

            if !goal.is_empty() {
                goals.push(Goal {
                    description: goal.to_string(),
                });
            }
        }

        if goals.is_empty() {
            goals.push(Goal {
                description: prompt.to_string(),
            });
        }

        goals
    }
}
