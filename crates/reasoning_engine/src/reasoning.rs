use crate::{
    CapabilityAnalyzer,
    IntentAnalyzer,
    ReasoningPlanner,
    ReasoningResult,
    ReflectionEngine,
    StrategySelector,
    TaskDecomposer,
    Verifier,
};
pub struct ReasoningEngine {
    analyzer: IntentAnalyzer,
    decomposer: TaskDecomposer,
    capability_analyzer: CapabilityAnalyzer,
    planner: ReasoningPlanner,
    reflection: ReflectionEngine,
    verifier: Verifier,
}
impl ReasoningEngine {
    pub fn new() -> Self {
        Self {
            analyzer: IntentAnalyzer::new(),
            decomposer: TaskDecomposer::new(),
            capability_analyzer: CapabilityAnalyzer::new(),
	    planner: ReasoningPlanner::new(),
            reflection: ReflectionEngine::new(),
            verifier: Verifier::new(),
        }
    }

    pub fn reason(&self, prompt: &str) -> ReasoningResult {
        let intent = self.analyzer.analyze(prompt);

        let strategy = StrategySelector::select(&intent);

	let mut goals = self.decomposer.decompose(prompt);

	for goal in &mut goals {
    		goal.capabilities = self.capability_analyzer.detect(goal);
	}

        let plan = self.planner.create_plan(goals.clone());

        let reflection = self.reflection.reflect(&plan);
        let verification = self.verifier.verify(&plan);

        let _ = reflection;
        let _ = verification;

        ReasoningResult {
            intent,
            strategy,
            goals,
        }
    }
}
impl Default for ReasoningEngine {
    fn default() -> Self {
        Self::new()
    }
}
