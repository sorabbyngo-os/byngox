use crate::{
    ExecutionDecision,
    ExecutionPolicy,
    SystemResources,
};

pub struct ResourceManager;

impl ResourceManager {

    pub fn new() -> Self {

        Self

    }

    pub fn evaluate(

        &self,

        resources: &SystemResources,

    ) -> ExecutionDecision {

        if resources.battery_percent < 10 {

            return ExecutionDecision {

                allow_execution: true,

                policy: ExecutionPolicy::LowPower,

            };

        }

        if resources.temperature_celsius > 85.0 {

            return ExecutionDecision {

                allow_execution: false,

                policy: ExecutionPolicy::Emergency,

            };

        }

        if resources.cpu_usage_percent > 90.0 {

            return ExecutionDecision {

                allow_execution: true,

                policy: ExecutionPolicy::Balanced,

            };

        }

        ExecutionDecision {

            allow_execution: true,

            policy: ExecutionPolicy::HighPerformance,

        }

    }

}
