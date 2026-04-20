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

| Tier | Models | Runtime | Condition |
|---|---|---|---|
| Tier 1 | Phi-4 Mini, Gemma 3 2B, SmolLM2 | llama.cpp / Ollama | Always-on, no internet |
| Tier 2 | Gemma 3 4B, Phi-4 INT8 | Ollama | GPU/NPU devices |
| Tier 3 | Qwen 2.5 72B INT4, Mistral Small 3.1 | Ollama | Performance devices |
| Tier 4 | DeepSeek-R1 70B, Mixtral 8x22B, LLaMA 3.1 70B | Byngox Prime vLLM | Self-hosted H100/A100 |

**Tier 4 = Byngox Prime** — a privately operated inference cluster.  
No external API keys. No data leaves Sorabbyngo infrastructure.

### Clinical Intelligence (Novela integration)
| Model | Role |
|---|---|
| GatorTron | Clinical NLP — trained on 90B words of EHR data |
| Meditron-70B | Clinical decision support, medical guidelines |
| BioMistral | Medical reasoning, drug interactions |
| ClinicalT5 | Structured output: SOAP notes, discharge summaries |

## Stack
- Python 3.12 + FastAPI
- NATS JetStream (ACP transport)
- LanceDB (vector store, offline-first)
- Neo4j (medical knowledge graph)
- ONNX Runtime (local inference)

**Sorabbyngo Company** — Kisii, Kenya | 2026
