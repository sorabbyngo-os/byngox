use std::collections::{HashMap, HashSet};

use agent_planner::{ExecutionPlan, PlanStep};

pub struct Scheduler;

impl Scheduler {
    pub fn schedule(plan: &ExecutionPlan) -> Vec<PlanStep> {
        let mut ordered = Vec::new();

        let mut completed = HashSet::<String>::new();

        let mut remaining: HashMap<String, PlanStep> = plan
            .steps
            .iter()
            .cloned()
            .map(|step| (step.id.clone(), step))
            .collect();

        while !remaining.is_empty() {
            let ready: Vec<String> = remaining
                .iter()
                .filter(|(_, step)| step.dependencies.iter().all(|d| completed.contains(d)))
                .map(|(id, _)| id.clone())
                .collect();

            assert!(
                !ready.is_empty(),
                "Dependency cycle detected in execution plan."
            );

            for id in ready {
                let step = remaining.remove(&id).unwrap();

                completed.insert(step.id.clone());

                ordered.push(step);
            }
        }

        ordered
    }
}
