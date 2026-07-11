use tool_executor::ToolExecutor;

#[test]
fn shell_tool_executes() {
    let executor = ToolExecutor::new();

    let result = executor.execute("shell", "echo hello").unwrap();

    assert!(result.success);
    assert!(result.output.contains("hello"));
}
