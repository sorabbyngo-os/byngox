use crate::Capability;

pub struct ToolClassifier;

impl ToolClassifier {
    pub fn classify(goal: &str) -> Capability {
        let goal = goal.to_lowercase();

        if goal.contains("read") || goal.contains("file") || goal.contains("directory") {
            return Capability::Filesystem;
        }

        if goal.contains("web") || goal.contains("search") || goal.contains("browse") {
            return Capability::Web;
        }

        if goal.contains("shell") || goal.contains("command") {
            return Capability::Shell;
        }

        if goal.contains("memory") || goal.contains("remember") {
            return Capability::Memory;
        }

        Capability::Reasoning
    }
}
