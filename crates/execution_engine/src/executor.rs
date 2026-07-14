use std::time::SystemTime;

use agent_planner::ExecutionPlan;

use crate::{
    ExecutionContext, ExecutionRecord, ExecutionRequest, ExecutionResult, ExecutionState,
    HistoryStore, RuntimeRegistry, event_bus::EventBus, runtimes::LocalRuntime,
    scheduler::Scheduler,
};

pub struct Executor {
    runtimes: RuntimeRegistry,
    history: HistoryStore,
    event_bus: EventBus,
}

impl Executor {
    pub fn new() -> Self {
        let mut runtimes = RuntimeRegistry::new();

        runtimes.register(Box::new(LocalRuntime::new()));

        Self {
            runtimes,
            history: HistoryStore::new(),
            event_bus: EventBus::new(),
        }
    }

    pub fn history(&self) -> &HistoryStore {
        &self.history
    }

    pub fn event_bus(&self) -> &EventBus {
        &self.event_bus
    }

    pub fn execute(
        &mut self,
        plan: &ExecutionPlan,
        context: &ExecutionContext,
    ) -> Vec<ExecutionResult> {
        let mut results = Vec::new();

        let steps = Scheduler::schedule(plan);

        let runtime = self
            .runtimes
            .runtime("local")
            .expect("local runtime not registered");

        for step in steps {
            let request = ExecutionRequest {
                target: step.target.clone(),
                operation: format!("{:?}", step.action),
                input: step.input.clone(),
            };

            let started = SystemTime::now();

            let result = runtime.execute(context, &request);

            let duration = started.elapsed().unwrap_or_default();

            let state = if result.success {
                ExecutionState::Completed
            } else {
                ExecutionState::Failed
            };

            self.history.push(ExecutionRecord {
                step_id: step.id.clone(),
                runtime: runtime.name().to_string(),
                target: request.target.clone(),
                operation: request.operation.clone(),
                state,
                started,
                duration,
                success: result.success,
                output: result.output.clone(),
            });

            results.push(result);
        }

        results
    }
}

impl Default for Executor {
    fn default() -> Self {
        Self::new()
    }
}
