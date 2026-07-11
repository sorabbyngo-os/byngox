use crate::Goal;

#[derive(Debug, Clone)]
pub struct GoalNode {
    pub goal: Goal,
    pub dependencies: Vec<usize>,
}

#[derive(Debug, Clone)]
pub struct GoalGraph {
    pub nodes: Vec<GoalNode>,
}

impl GoalGraph {
    pub fn new() -> Self {
        Self {
            nodes: Vec::new(),
        }
    }

    pub fn add_goal(
        &mut self,
        goal: Goal,
    ) -> usize {

        let index = self.nodes.len();

        self.nodes.push(
            GoalNode {
                goal,
                dependencies: Vec::new(),
            },
        );

        index
    }

    pub fn add_dependency(
        &mut self,
        node: usize,
        depends_on: usize,
    ) {

        self.nodes[node]
            .dependencies
            .push(depends_on);
    }
}
