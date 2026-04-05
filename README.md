# Byngox
> **8-Agent Swarm Reasoning Engine** — Sorabbyngo Labs

The cognitive intelligence core of SORABBYNGO OS. Six health-specialized agents plus network and learning coordination, communicating via ACP over NATS JetStream.

## Agents
| Agent | Role |
|---|---|
| health_agent | Clinical decision support, triage |
| drug_agent | Medication verification, counterfeit detection |
| context_agent | Patient history, episodic memory |
| network_agent | Byngonet coordination, distributed tasks |
| learning_agent | Feedback loops, model improvement |
| population_agent | Epidemiology, outbreak detection, heatmaps |

## Intelligence Tiers
- Tier 1: Phi-3 mini / Qwen 3B — always offline
- Tier 2: LLaMA 3 8B / Mixtral — GPU/NPU
- Tier 3: Claude API + PRIME LoRA adapters — cloud

## Stack
- Python 3.12 + FastAPI
- NATS JetStream (ACP transport)
- LanceDB (vector store, offline-first)
- Neo4j (medical knowledge graph)
- ONNX Runtime (local inference)

**Sorabbyngo Company** — Kisii, Kenya | 2026
