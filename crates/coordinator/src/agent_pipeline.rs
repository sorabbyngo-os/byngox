use crate::AgentSession;
use agent_planner::AgentPlanner;
use execution_engine::{ExecutionContext, Executor, ExecutionResult};
use reasoning_engine::ReasoningEngine;

pub struct AgentPipeline {
    reasoning: ReasoningEngine,
    planner: AgentPlanner,
    executor: Executor,
}

impl AgentPipeline {
    pub fn new() -> Self {
        Self {
            reasoning: ReasoningEngine::new(),
            planner: AgentPlanner::new(),
            executor: Executor::new(),
        }
    }
    pub fn execute(
    	&mut self,
    	session: &AgentSession,
    	prompt: &str,
    ) -> Vec<ExecutionResult> {
    	let _ = session;

    	let reasoning = self.reasoning.reason(prompt);

    	let plan = self.planner.create_plan_from_reasoning(&reasoning);

    	let context = ExecutionContext::default();

    	self.executor.execute(&plan, &context)
    }
}

impl Default for AgentPipeline {
    fn default() -> Self {
        Self::new()
    }
}
