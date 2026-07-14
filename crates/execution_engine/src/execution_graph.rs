use std::collections::HashMap;

use agent_planner::PlanStep;

#[derive(Debug, Clone)]
pub struct ExecutionGraph {
    pub nodes: HashMap<String, PlanStep>,
    pub children: HashMap<String, Vec<String>>,
}
