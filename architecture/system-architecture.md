# Sorabbyngo OS Ecosystem Status

**Engineering Architecture Update — June 2026**

---

# Purpose

This document defines the current architecture of the Sorabbyngo ecosystem after the latest engineering decisions. It is intended to guide all contributors and keep every repository aligned as development scales.

---

# High-Level Architecture

```
                     USER
          Voice • Touch • Keyboard
                    │
                    ▼
               CHAMEHA
      Personality • Conversation
      Intent • AION Runtime
                    │
                    ▼
               BYNGOX
     Multi-Agent Cognitive Engine
                    │
                    ▼
        Capability & Hardware APIs
                    │
        ┌───────────┴────────────┐
        │                        │
        ▼                        ▼
Hardware Agent             Byngonet
(Device Knowledge)       Networking Layer
        │                        │
        └───────────┬────────────┘
                    ▼
          Sorabbyngo Base
     Immutable Fedora Foundation
                    │
                    ▼
               Linux Kernel
                    │
                    ▼
                Hardware
```

---

# Repository Responsibilities

## Chameha

Repository:

```
sorabbyngo-os/chameha
```

Purpose:

Chameha is the user-facing AI.

It is responsible for:

* Voice interaction
* Chat interaction
* Personality
* Long-term conversations
* Intent understanding
* User preferences
* Memory access
* Running the AION runtime
* Request orchestration

Users never interact directly with Byngox.

To the user there is only **Chameha**.

---

## AION

AION is **not a standalone repository.**

AION lives inside Chameha.

Responsibilities:

* Device orchestration
* Intent execution
* Hardware control
* Capability planning
* Safe execution
* Scheduling
* Action verification

AION converts:

```
User Intent
      ↓
Execution Plan
      ↓
Byngox
      ↓
Operating System
```

---

## Byngox

Repository:

```
sorabbyngo-os/byngox
```

Purpose:

Distributed reasoning engine.

Byngox never communicates with users.

Responsibilities:

* Multi-agent reasoning
* Planning
* Context analysis
* Medical reasoning
* Learning
* Security reasoning
* Risk evaluation
* Decision aggregation

Current architecture:

```
Coordination Agent

├── Health
├── Drug
├── Learning
├── Population
├── Security
├── Context
├── Network
├── Hardware
```

The new **Hardware Agent** becomes a first-class agent.

---

## Hardware Agent

New agent inside Byngox.

Purpose:

Maintain complete awareness of the current device.

It continuously understands:

CPU

GPU

RAM

Battery

Thermals

Storage

Network

Sensors

Camera

Microphone

Power source

Display

Accelerators

Running workloads

Resource limits

Hardware health

Example:

```
User:

Train this model.

↓

Hardware Agent

RTX 3050
8 GB RAM

↓

Byngox

Chooses quantized model

↓

AION executes safely.
```

Another example:

```
User:

Render a 4K video.

↓

Hardware Agent

Battery = 5%

↓

Reject or delay operation.
```

This prevents the AI from damaging the device or making unrealistic decisions.

---

## Byngonet

Repository:

```
sorabbyngo-os/byngonet
```

Updated mission:

Byngonet is **NOT an AI.**

AI responsibilities have moved into Byngox.

Byngonet becomes the networking backbone.

Responsibilities:

* Device discovery
* Mesh networking
* Offline synchronization
* Node identity
* Secure communication
* Peer routing
* Remote execution transport
* Network health
* Presence
* Service discovery
* File synchronization
* Session transport
* Multi-device communication

Think of it as:

```
AI decides

↓

Byngonet transports
```

Not

```
Byngonet thinks.
```

---

## Sorabbyngo Base

Repository:

```
sorabbyngo-base-kernel/sorabbyngo-base
```

Purpose:

Operating system foundation.

Contains:

* Fedora Silverblue
* bootc
* rpm-ostree
* Kernel patches
* Security
* Runtime
* APIs
* Core services

No AI logic belongs here.

It only exposes capabilities.

---

# Remote Device Control

Remote execution now follows this chain.

```
User

↓

Chameha

↓

AION

↓

Capability Broker

↓

Byngonet

↓

Target Device

↓

Hardware APIs

↓

Result

↓

Back to User
```

The user never configures SSH.

No command lines.

No terminal access.

Everything is capability-based.

---

# Capability Model

Applications never receive unrestricted hardware access.

Instead:

```
Application

↓

Capability Broker

↓

Permission Engine

↓

Hardware API

↓

Hardware
```

Every action is:

* authenticated
* authorized
* audited
* revocable

---

# Current Engineering Principles

1. Chameha is the only user-facing AI.

2. AION lives inside Chameha.

3. Byngox performs reasoning only.

4. Hardware knowledge belongs to the Hardware Agent.

5. Byngonet handles networking only.

6. Sorabbyngo Base contains no AI.

7. Every hardware action passes through the Capability Broker.

8. Remote device control is capability-based, not SSH-based.

9. AI decisions are always constrained by actual device capabilities.

10. Desktop and Mobile are the first supported platforms.

---

# Current Repository Status

```
sorabbyngo-base
        │
        ├── Fedora Silverblue
        ├── bootc
        ├── Security
        ├── Runtime
        ├── APIs
        └── Core Services

                ▲

        Byngonet
(Network & Connectivity)

                ▲

        Hardware Agent
(Device Awareness)

                ▲

            Byngox
(Reasoning Engine)

                ▲

      Chameha + AION
(User Experience)

                ▲

              User
```

---

# Development Priority

Current roadmap:

**Phase 1**

* Sorabbyngo Base
* Core services
* Capability Broker
* Permission Engine

**Phase 2**

* Hardware Agent
* Byngonet transport
* Device APIs

**Phase 3**

* AION integration
* Remote control
* Automation

**Phase 4**

* Sorabbyngo Mobile

**Phase 5**

* Sorabbyngo Desktop

This document supersedes earlier designs where networking intelligence resided inside Byngonet. Intelligence is now centralized in Byngox, while networking, transport, and synchronization remain the responsibility of Byngonet.
