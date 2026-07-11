use agent_planner::AgentPlanner;
use reasoning_engine::{Goal, Intent, ReasoningResult, ReasoningStrategy};

#[test]
fn translates_reasoning_into_execution_plan() {
    let planner = AgentPlanner::new();

    let reasoning = ReasoningResult {
        intent: Intent::ToolUse,
        strategy: ReasoningStrategy::Planning,
        goals: vec![Goal {
            description: "read config".into(),
        }],
    };

    let plan = planner.create_plan_from_reasoning(&reasoning);

    assert_eq!(plan.steps.len(), 2);
    assert_eq!(plan.steps[0].target, "filesystem");
    assert_eq!(plan.steps[1].action, agent_planner::AgentAction::Respond);
}
