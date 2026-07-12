use agent_planner::ToolClassifier;
use tool_capability::ToolCapability;

#[test]
fn classify_filesystem() {
    assert_eq!(
        ToolClassifier::classify("read config file"),
        ToolCapability::Filesystem
    );
}

#[test]
fn classify_web() {
    assert_eq!(
        ToolClassifier::classify("search the web"),
        ToolCapability::Web
    );
}

#[test]
fn classify_shell() {
    assert_eq!(
        ToolClassifier::classify("run shell command"),
        ToolCapability::Shell
    );
}

#[test]
fn classify_reasoning() {
    assert_eq!(
        ToolClassifier::classify("explain recursion"),
        ToolCapability::Reasoning
    );
}

//fn classify_memory() {
//  assert_eq!(
//    ToolClassifier::classify("check memmory"),
//  ToolCapability::memory
// );
//}
