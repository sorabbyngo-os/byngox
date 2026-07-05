#[derive(Debug)]

pub enum ProviderError {

    ProviderNotFound,

    ProviderUnavailable,

    InitializationFailed,

    InferenceFailed,

}
