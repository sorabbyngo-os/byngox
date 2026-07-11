use agent_planner::{Capability, ToolClassifier};

#[test]
fn classify_filesystem() {
    assert_eq!(
        ToolClassifier::classify("read config file"),
        Capability::Filesystem
    );
}

#[test]
fn classify_web() {
    assert_eq!(ToolClassifier::classify("search the web"), Capability::Web);
}

#[test]
fn classify_shell() {
    assert_eq!(
        ToolClassifier::classify("run shell command"),
        Capability::Shell
    );
}

#[test]
fn classify_reasoning() {
    assert_eq!(
        ToolClassifier::classify("explain recursion"),
        Capability::Reasoning
    );
}
