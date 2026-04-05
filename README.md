# ClearPath — Migrant Worker Rights Agent

An AI agent built on OpenClaw + Agnes-1.5-Pro that helps migrant workers in Singapore file workplace complaints automatically.

## The Problem
Singapore has 1.5 million migrant workers. When underpaid, injured, or wrongfully dismissed, most never file a complaint. The process requires navigating MOM, TADM, and multiple English-only portals. Workers are scared, exhausted, and don't know where to start.

## What ClearPath Does
- Worker sends a payslip PDF or describes their situation on Telegram
- Agnes reads the document and extracts all details automatically
- Collects any missing information one question at a time
- Generates a complete formal TADM complaint file
- Notifies NGO caseworker instantly via Telegram
- Fires complaint email to TADM automatically
- If no response in 24 hours — Agnes escalates automatically. Nobody asked it to.

## How It Works
1. Worker messages @clearpathworker_bot on Telegram
2. Worker sends payslip PDF or answers questions
3. Agnes extracts: name, FIN, employer, UEN, problem type, amount, months, evidence
4. Case file generated automatically
5. Caseworker notified on Telegram
6. Complaint fired to TADM
7. Worker receives confirmation

## Tech Stack
- **Agnes-1.5-Pro** (via ZenMux API) — AI brain for vision, reasoning, and autonomous action
- **OpenClaw v2026.4.2** — agent framework handling Telegram, memory, scheduling, tool execution
- **Telegram Bot API** — worker and caseworker interfaces
- **HEARTBEAT.md** — autonomous 24-hour escalation scheduler
- **Pipedream** — webhook simulating TADM email submission (production: real TADM API)

## Key Files
- `openclaw.json` — OpenClaw configuration, model provider, Telegram setup
- `SOUL.md` — ClearPath's personality, rules, and case collection workflow
- `HEARTBEAT.md` — Scheduled escalation tasks

## Try It
Text @clearpathworker_bot on Telegram

## Built At
Agnes AI × WAVE × NUSSU commIT OpenClaw Hackathon 2026
