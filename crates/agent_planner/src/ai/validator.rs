use crate::ai::{
    PlannerAction,
    PlannerOutput,
};

pub struct PlannerValidator;

impl PlannerValidator {

    pub fn validate(
        plan: &PlannerOutput,
    ) -> bool {

        if plan.steps.is_empty() {
            return false;
        }

        for step in &plan.steps {

            match step.action {

                PlannerAction::Tool => {

                    if step.tool.is_none() {
                        return false;
                    }

                    if step.input.is_none() {
                        return false;
                    }
                }

                PlannerAction::Respond => {}

                PlannerAction::Finish => {}
            }
        }

        true
    }
}
