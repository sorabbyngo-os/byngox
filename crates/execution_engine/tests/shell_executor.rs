use execution_engine::{ExecutionRequest, ShellExecutor, ToolExecutor};

#[test]
fn shell_executor_runs_command() {
    let executor = ShellExecutor;

    let request = ExecutionRequest {
        target: "shell".into(),
        operation: "run".into(),
        input: "echo hello".into(),
    };

    let result = executor.execute(&request);

    assert!(result.success);
    assert!(result.output.contains("hello"));
}
