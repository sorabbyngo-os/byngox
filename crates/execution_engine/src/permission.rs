use crate::ExecutionRequest;

#[derive(Debug, Clone)]
pub enum PermissionDecision {
    Allow,
    Deny(String),
}

pub trait PermissionEngine: Send + Sync {
    fn authorize(&self, request: &ExecutionRequest) -> PermissionDecision;
}

pub struct DefaultPermissionEngine;

impl PermissionEngine for DefaultPermissionEngine {
    fn authorize(&self, _request: &ExecutionRequest) -> PermissionDecision {
        PermissionDecision::Allow
    }
}
