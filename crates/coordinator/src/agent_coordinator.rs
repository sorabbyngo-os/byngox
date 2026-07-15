use execution_engine::ExecutionResult;
use crate::agent_session::AgentSession;
use crate::agent_pipeline::AgentPipeline;

pub struct AgentCoordinator {
    session: AgentSession,
    pipeline: AgentPipeline,
}

impl AgentCoordinator {
    pub fn new() -> Self {
    Self {
        session: AgentSession::new(),
        pipeline: AgentPipeline::new(),
     }
   }
   pub fn execute(
     &mut self,
     prompt: impl AsRef<str>,
   ) -> Vec<ExecutionResult> {
     self.pipeline.execute(&self.session, prompt.as_ref())
   }
}

impl Default for AgentCoordinator {
    fn default() -> Self {
        Self::new()
    }
}
