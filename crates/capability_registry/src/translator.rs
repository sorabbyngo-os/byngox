let capability = ToolClassifier::classify(&goal.description);

let provider = self
    .provider_registry
    .resolve(capability)
    .expect("missing provider");
