# Hardware Agent

The Hardware Agent reasons about device capabilities.

It does not control hardware.

Responsibilities

- Read hardware profile
- Estimate available resources
- Evaluate CPU load
- Evaluate GPU load
- Evaluate battery state
- Evaluate thermal limits
- Choose execution strategy
- Recommend resource allocation

Execution is delegated to the AI Hardware Controller.
