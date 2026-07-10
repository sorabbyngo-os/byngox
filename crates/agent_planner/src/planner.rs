use crate::{
    AgentAction,
    ExecutionPlan,
    PlanStep,
};

pub struct AgentPlanner;

impl AgentPlanner {

    pub fn new() -> Self {
        Self
    }

    fn add_tool_step(
    	plan: &mut ExecutionPlan,
    	tool: &str,
    	input: &str,
    ) {
       plan.add_step(
        PlanStep {
            action: AgentAction::UseTool,
            target: tool.to_string(),
            input: input.trim().to_string(),
        }
      );
    }

    pub fn create_plan(
        &self,
        prompt: &str,
    ) -> ExecutionPlan {

        let mut plan = ExecutionPlan::new();

        if let Some(command) = prompt.strip_prefix("shell:") {

	    Self::add_tool_step(
    		&mut plan,
    		"shell",
    		command,
	    );

            plan.add_step(
                PlanStep {
                    action: AgentAction::Respond,
                    target: String::new(),
                    input: String::new(),
                }
            );

            return plan;
        }

        if let Some(path) = prompt.strip_prefix("read:") {

	    Self::add_tool_step(
    		&mut plan,
    		"filesystem",
    		path,
	    );

            plan.add_step(
                PlanStep {
                    action: AgentAction::Respond,
                    target: String::new(),
                    input: String::new(),
                }
            );

            return plan;
        }

        if let Some(query) = prompt.strip_prefix("web:") {

	    Self::add_tool_step(
    		&mut plan,
    		"web",
    		query,
	    );

            plan.add_step(
                PlanStep {
                    action: AgentAction::Respond,
                    target: String::new(),
                    input: String::new(),
                }
            );

            return plan;
        }

	if prompt.to_lowercase().starts_with("read ") {
    	 let path = prompt[5..].trim();

    	 Self::add_tool_step(
         	&mut plan,
        	"filesystem",
        	path,
         );

   	 plan.add_step(
             PlanStep {
            	action: AgentAction::Respond,
            	target: String::new(),
            	input: String::new(),
            }
    	);

    	return plan;
       }

        plan.add_step(
            PlanStep {
                action: AgentAction::Respond,
                target: String::new(),
                input: String::new(),
            }
        );

        plan
    }

}
