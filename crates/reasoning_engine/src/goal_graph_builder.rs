use crate::{
    Goal,
    GoalGraph,
};

pub struct GoalGraphBuilder;

impl GoalGraphBuilder {
    pub fn new() -> Self {
        Self
    }

    pub fn build(
        &self,
        goals: Vec<Goal>,
    ) -> GoalGraph {

        let mut graph = GoalGraph::new();

        let mut previous = None;

        for goal in goals {

            let current = graph.add_goal(goal);

            if let Some(prev) = previous {
                graph.add_dependency(current, prev);
            }

            previous = Some(current);
        }

        graph
    }
}
