use crate::{
    IntentAnalyzer, ReasoningPlanner, ReasoningResult, ReflectionEngine, StrategySelector,
    TaskDecomposer, Verifier,
};

pub struct ReasoningEngine {
    analyzer: IntentAnalyzer,
    decomposer: TaskDecomposer,
    planner: ReasoningPlanner,
    reflection: ReflectionEngine,
    verifier: Verifier,
}

impl ReasoningEngine {
    pub fn new() -> Self {
        Self {
            analyzer: IntentAnalyzer::new(),
            decomposer: TaskDecomposer::new(),
            planner: ReasoningPlanner::new(),
            reflection: ReflectionEngine::new(),
            verifier: Verifier::new(),
        }
    }

    pub fn reason(&self, prompt: &str) -> ReasoningResult {
        let intent = self.analyzer.analyze(prompt);

        let strategy = StrategySelector::select(&intent);

        let goals = self.decomposer.decompose(prompt);

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
