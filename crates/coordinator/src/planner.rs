use crate::{CoordinatorError, ExecutionPlan, InferenceTask};
use benchmark_engine::BenchmarkEngine;
use capability_registry::CapabilityRegistry;
use model_registry::ModelRegistry;
use model_router::ModelRouter;
use resource_manager::ResourceManager;
pub struct Planner {
    capability_registry: CapabilityRegistry,

    model_registry: ModelRegistry,

    benchmark_engine: BenchmarkEngine,

    resource_manager: ResourceManager,

    router: ModelRouter,
}

impl Planner {
    pub fn new() -> Self {
        Self {
            capability_registry: CapabilityRegistry::new(),

            model_registry: ModelRegistry::new(),

            benchmark_engine: BenchmarkEngine::new(),

            resource_manager: ResourceManager::new(),

            router: ModelRouter::new(),
        }
    }
    pub fn plan(&self, task: &InferenceTask) -> Result<ExecutionPlan, CoordinatorError> {
        // STEP 1
        let definition = self
            .capability_registry
            .resolve(&task.capability)
            .ok_or(CoordinatorError::CapabilityNotFound)?;
        //step 2
        let candidates = self.model_registry.models_for(&definition.capability);

        // STEP 3
        let ranked = self.benchmark_engine.rank(candidates);

        // STEP 4
        let available = self.resource_manager.filter(ranked);

        // STEP 5
        let selected = self
            .router
            .select(available)
            .ok_or(CoordinatorError::NoModelAvailable)?;

        Ok(ExecutionPlan {
            selection: selected.selection,

            capability: definition.id.clone(),

            requires_context: false,

            requires_memory: false,
        })
    }
}
