use tool_capability::ToolCapability;
pub struct ToolClassifier;

impl ToolClassifier {
    pub fn classify(goal: &str) -> ToolCapability {
        let goal = goal.to_lowercase();

        if goal.contains("read") || goal.contains("file") || goal.contains("directory") {
            return ToolCapability::Filesystem;
        }

        if goal.contains("web") || goal.contains("search") || goal.contains("browse") {
            return ToolCapability::Web;
        }

        if goal.contains("shell") || goal.contains("command") {
            return ToolCapability::Shell;
        }

        if goal.contains("memory") || goal.contains("remember") {
            return ToolCapability::Memory;
        }

        ToolCapability::Reasoning
    }
}
