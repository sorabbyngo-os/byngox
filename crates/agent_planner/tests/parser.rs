use agent_planner::{PlannerParser, PlannerValidator};

#[test]
fn parse_plan() {
    let json = r#"
    {
        "steps":[
            {
                "action":"tool",
                "tool":"filesystem",
                "input":"README.md"
            },
            {
                "action":"respond"
            }
        ]
    }
    "#;

    let plan = PlannerParser::parse(json).unwrap();

    assert!(PlannerValidator::validate(&plan));
}
