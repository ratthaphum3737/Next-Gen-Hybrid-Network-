# Next-Gen Hybrid Network

# 🛰️ IDMS — Interstellar Data Mesh Simulator

> A Python-based simulation of a Delay/Disruption Tolerant Networking (DTN) system for deep-space communication, featuring QoS priority queuing, Packet Loss Guard, Auto-flush Buffer, and HITL Governance.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Sprint](https://img.shields.io/badge/Sprint-Beta--Sprint3%2F4-orange)
![Tests](https://img.shields.io/badge/Tests-pytest-brightgreen)
![CI](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue?logo=github)

---

## 📡 Project Overview

Traditional TCP/IP protocols are ineffective in deep-space environments due to extreme latency and frequent signal disruptions. **IDMS** simulates a decentralized mesh network of space nodes that communicate asynchronously using the **Bundle Protocol (DTN)**, enabling:

- ✅ Automatic rerouting when primary links fail
- ✅ Store-and-Forward buffering with zero data loss
- ✅ QoS-based priority queuing (Critical → Scientific → Media)
- ✅ **P1 Critical Packet Loss Guard** — never dropped regardless of link quality
- ✅ **Auto-flush Buffer** — forwards automatically when node comes back Online
- ✅ **HITL Double-approve Guard** — prevents race condition on human approvals
- ✅ Hybrid Optical/RF failover at the Data Link layer

---

## 🏗️ System Architecture

| Node | Abbr | Role |
|------|------|------|
| **Earth Mission Control** | EMC | Central command hub |
| **Lunar Gateway Relay** | LGR | Mid-path satellite router |
| **Surface Base LAN** | SBL | Local Ethernet network on lunar base |
| **Deep Space Probe** | DSP | Deep-space vessel, highest disruption risk |

### Communication Channels

- **Primary Link (Optical/Laser):** 260 Mbps (ref: Artemis II O2O system)
- **Secondary Link (Radio Frequency):** Auto-activated fallback

---

## ⚙️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Core language |
| `pytest` | Unit & Integration Testing |
| GitHub Actions | CI/CD — auto-test on push/PR to main |

---

## 📦 Module Breakdown

### Module 1 — Network Node Environment (`space_node.py`)
- `SpaceNode` class with `is_online` **property setter** (ISS-02: auto-flush)
- `loss_rate` parameter for link simulation (ISS-01)
- `_hitl_pending` flag for HITL double-approve guard (ISS-05)

### Module 2 — Link Delay & Disruption Engine (`simulation.py`)
- Latency simulator (Earth–Moon RTT ≈ 2.6s)
- Packet Loss mechanics with **P1 Critical bypass**

### Module 3 — DTN Store-and-Forward Logic
- `storage_buffer` per node — persistent until delivery
- **Auto-flush** triggered by `is_online: False → True` (ISS-02)

### Module 4 — QoS & Traffic Management
- Priority Queue: `1-Critical → 2-Scientific → 3-Media`
- **FIFO Tie-breaking** by timestamp when priority equal (ISS-03)

---

## 🐛 Sprint Beta — Issues Fixed (Sprint 3)

| Issue | Module | Fix |
|-------|--------|-----|
| **ISS-01** | Module 2 | P1 Critical bypasses Packet Loss drop — `if priority == 1: bypass` |
| **ISS-02** | Module 1 | `is_online` property setter triggers `process_buffer()` on `False→True` |
| **ISS-03** | Module 4 | FIFO tie-breaking confirmed: `sort(key=lambda x: (x[0], x[1]))` ✅ |
| **ISS-05** | Module 1 | `_hitl_pending` flag blocks double-approve race condition |
| **ISS-06** | CI/CD | `.github/workflows/main.yml` — auto-test on push & PR to main |

---

## 🚀 Getting Started

### Prerequisites
```bash
pip install pytest pytest-cov
```

### 1. รัน Terminal Simulation
```bash
cd idms
python simulation.py
```

### 2. รัน Visual Dashboard (HTML)
```bash
# เปิดในเบราว์เซอร์ได้เลย ไม่ต้องติดตั้งอะไร
open dtn_v2.html          # macOS
start dtn_v2.html         # Windows
```

### 3. รัน Tests
```bash
cd idms
pytest test_idms.py -v
```

---

## 🧪 Test Cases

| TC | Test Case | AC | Status |
|----|-----------|-----|--------|
| TC-01 | Normal Transmission (3+ nodes) | AC-1 | ✅ |
| TC-02 | Single Node Failure | AC-2 | ✅ |
| TC-03 | Full Recovery (Auto-flush) | AC-3 | ✅ |
| TC-04 | QoS Priority Order + FIFO | AC-4 | ✅ |
| TC-05 | Stress Test 90% Packet Loss | AC-5 | ✅ |
| TC-06 *(Bonus)* | Multi-node Failure + Reroute | — | ✅ |
| TC-07 *(Bonus)* | HITL Double-approve Guard | AC-6 | ✅ |

### ISS Test Cases (Sprint 3)

| Test | Issue | Description |
|------|-------|-------------|
| `test_iss01_critical_bypass_drop` | ISS-01 | P1 Critical ไม่ถูก drop แม้ loss_rate=100% |
| `test_iss01_non_critical_can_drop` | ISS-01 | P3 Media ถูก drop ตาม loss_rate |
| `test_iss02_auto_flush_on_online` | ISS-02 | Buffer flush อัตโนมัติเมื่อ is_online=True |
| `test_tc04_fifo_same_priority` | ISS-03 | FIFO รักษาลำดับ timestamp |
| `test_tc07_hitl_double_approve_blocked` | ISS-05 | Double-approve ถูก block |

---

## ✅ Acceptance Criteria

| AC | Criteria | TC | Verified |
|----|----------|----|---------|
| AC-1 | ≥3 nodes Normal Transmission | TC-01 | ✅ |
| AC-2 | Node Offline → 0% Data Loss | TC-02 | ✅ |
| AC-3 | Node Online → Auto-forward | TC-03 | ✅ |
| AC-4 | P1 Critical forwards before P2/P3 | TC-04 | ✅ |
| AC-5 | pytest 0 FAILED | TC-05 | ✅ |
| AC-6 *(Extra)* | HITL no double-send | TC-07 | ✅ |

---

## 📂 File Structure

```
📁 idms/
  ├── space_node.py               ← Module 1,3,4 + ISS-01,02,03,05 fixes
  ├── simulation.py               ← Module 2 + demo all scenarios
  ├── test_idms.py                ← pytest TC-01 to TC-07 (+ ISS tests)
  ├── dtn_v2.html                 ← Visual Interactive Dashboard
  └── README.md                   ← This file

📁 .github/
  └── workflows/
      └── main.yml                ← ISS-06: CI/CD auto-test on push/PR
```

---

## 👥 Team

| Role | Responsibilities |
|------|-----------------|
| Architect | System design, Architecture Spec, Merge Review |
| Engineer | ISS-01,02,03,05 fixes, Multi-hop DTN, Code Docs |
| Specialist | Space domain research, Latency/RTT validation |
| DevOps | ISS-06 CI/CD, Branch Protection, Tag v1.0.0 |
| Tester/QA | TC-01 to TC-07, Regression Test, Final Report |

---

## 📅 Sprint Summary

| Sprint | Milestone | Status |
|--------|-----------|--------|
| Alpha Week 1 | Foundation & Environment | ✅ Done |
| Alpha Week 2 | Core Routing & Disruption | ✅ Done |
| **Beta Sprint 3** | Fix Issues ISS-01~06 | ✅ Done |
| **Beta Sprint 4** | Final QA & Pitch Prep | 🔄 In Progress |

---

## 📄 License

MIT License

# Next-Gen Hybrid Network VDIO
https://youtu.be/LFwEf5i-hxc

| ชื่อเล่น | รหัสนักศึกษา | ชื่อ–นามสกุล |
|--------|--------------|-------------|
| โอ๊ต | 653380373-7 | นายรัฐภูมิ แฝงฤทธิ์หลง |
| ดิว | 673380393–9 | นายกิตติพัฒน์ สีราช |
| ทีม | 673380404-0 | นายธนพัฒน์ พิมจำปา |
| ครีม | 673380401-6 | นางสาวชุตินันท์ หมายสุข |
| จ๋า | 673380419-7 | นางสาวภัทราพร ศรีชนะ |
