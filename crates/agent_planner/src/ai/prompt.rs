pub struct PlannerPrompt;

impl PlannerPrompt {
    pub fn build(user_prompt: &str) -> String {
        format!(
r#"You are the planning engine for ByngoX.

Available tools:

- filesystem
- shell
- web

Return ONLY valid JSON.

Example:

{{
  "steps":[
    {{
      "action":"tool",
      "tool":"filesystem",
      "input":"README.md"
    }},
    {{
      "action":"respond"
    }}
  ]
}}

User request:

{}
"#,
            user_prompt
        )
    }
}
