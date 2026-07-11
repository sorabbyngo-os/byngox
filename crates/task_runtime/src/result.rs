#[derive(Debug, Clone)]
pub struct TaskResult {
    pub success: bool,
    pub output: String,
}

impl TaskResult {
    pub fn success(output: impl Into<String>) -> Self {
        Self {
            success: true,
            output: output.into(),
        }
    }

    pub fn failure(output: impl Into<String>) -> Self {
        Self {
            success: false,
            output: output.into(),
        }
    }
}
