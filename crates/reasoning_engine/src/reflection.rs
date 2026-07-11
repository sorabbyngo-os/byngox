use crate::{Goal, ReasoningPlan};

#[derive(Debug, Clone)]
pub struct ReflectionResult {
    pub valid: bool,
    pub feedback: Vec<String>,
}

pub struct ReflectionEngine;

impl ReflectionEngine {
    pub fn new() -> Self {
        Self
    }

    pub fn reflect(&self, plan: &ReasoningPlan) -> ReflectionResult {
        let mut feedback = Vec::new();

        if plan.goals.is_empty() {
            feedback.push("No goals were produced.".to_string());
        }

        for Goal { description } in &plan.goals {
            if description.trim().is_empty() {
                feedback.push("Empty goal detected.".to_string());
            }
        }

        ReflectionResult {
            valid: feedback.is_empty(),

            feedback,
        }
    }
}
