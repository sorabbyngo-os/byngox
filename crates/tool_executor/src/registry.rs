use std::collections::HashMap;

use crate::{
    ShellTool,
    FilesystemTool,
    WebTool,
    Tool,
};

pub struct ToolRegistry {
    tools: HashMap<String, Box<dyn Tool>>,
}

impl ToolRegistry {
    pub fn new() -> Self {
        let mut registry = Self {
            tools: HashMap::new(),
        };

        registry.register(
            "shell",
            Box::new(ShellTool::new()),
        );

	registry.register(
    		"web",
    	  Box::new(WebTool::new()),
	);

	registry.register(
    		"filesystem",
    	  Box::new(FilesystemTool::new()),
	);

        registry
    }

    pub fn register(
        &mut self,
        name: impl Into<String>,
        tool: Box<dyn Tool>,
    ) {
        self.tools.insert(name.into(), tool);
    }

    pub fn get(
        &self,
        name: &str,
    ) -> Option<&dyn Tool> {
        self.tools.get(name).map(|t| t.as_ref())
    }
}
