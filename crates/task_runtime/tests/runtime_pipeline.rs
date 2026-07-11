use agent_planner::AgentPlanner;
use task_runtime::TaskRuntime;

#[test]
fn runtime_executes_plan() {
    let planner = AgentPlanner::new();

    let runtime = TaskRuntime::new();

    let plan = planner.create_plan("shell: echo hello");

    let result = runtime.execute(plan).unwrap();

    assert!(result.success);

    assert!(result.output.contains("hello"));
}
