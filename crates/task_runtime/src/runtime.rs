use agent_planner::{AgentAction, ExecutionPlan};

use tool_executor::{ToolError, ToolExecutor};

use crate::{ExecutionState, ProgressTracker, RunningTask, TaskResult, TaskScheduler, TaskStatus};

pub struct TaskRuntime {
    executor: ToolExecutor,
    scheduler: TaskScheduler,
}

impl TaskRuntime {
    pub fn new() -> Self {
        Self {
            executor: ToolExecutor::new(),
            scheduler: TaskScheduler::new(),
        }
    }

    pub fn execute(&self, plan: ExecutionPlan) -> Result<TaskResult, ToolError> {
        // Schedule the execution plan
        let scheduled_plan = self.scheduler.schedule(plan);

        // Create runtime state
        let mut state = ExecutionState::new(RunningTask::new(scheduled_plan));

        state.set_status(TaskStatus::Running);

        // Track execution progress
        let mut progress = ProgressTracker::new(state.task.plan.steps.len());

        let mut output = String::new();

        while !state.finished() {
            let step = &state.task.plan.steps[state.current_step()];

            match step.action {
                AgentAction::UseTool => {
                    let result = self.executor.execute(&step.target, &step.input)?;

                    output.push_str(&result.output);
                    output.push('\n');
                }

                AgentAction::Respond => {
                    // Nothing to execute
                }

                AgentAction::Finish => {
                    break;
                }
            }

            progress.advance();
            state.advance();
        }

        state.set_status(TaskStatus::Completed);

        println!(
            "Execution completed: {:.0}% ({}/{})",
            progress.percentage(),
            progress.completed(),
            progress.total(),
        );

        Ok(TaskResult::success(output))
    }
}
