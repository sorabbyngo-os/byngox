use crate::ai::PlannerOutput;

pub struct PlannerParser;

impl PlannerParser {
    pub fn parse(json: &str) -> Result<PlannerOutput, serde_json::Error> {
        serde_json::from_str(json)
    }
}
