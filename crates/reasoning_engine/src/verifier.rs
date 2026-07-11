use crate::ReasoningPlan;

#[derive(Debug, Clone)]
pub struct VerificationResult {
    pub verified: bool,
    pub errors: Vec<String>,
}

pub struct Verifier;

impl Verifier {
    pub fn new() -> Self {
        Self
    }

    pub fn verify(&self, plan: &ReasoningPlan) -> VerificationResult {
        let mut errors = Vec::new();

        if plan.goals.is_empty() {
            errors.push("Execution plan contains no goals.".to_string());
        }

        VerificationResult {
            verified: errors.is_empty(),
            errors,
        }
    }
}
