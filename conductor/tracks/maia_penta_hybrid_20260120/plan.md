# Implementation Plan: Maia Penta Hybrid Analysis

## Phase 1: Request & Response Schemas
- [x] **Red Phase**: Create test for new hybrid schemas (Input/Output)
- [x] **Green Phase**: Define `HybridAnalysisRequest` and `HybridAnalysisResponse` in `schemas/`
- [x] Task: Conductor - User Manual Verification 'Phase 1: Request & Response Schemas' (Protocol in workflow.md)

## Phase 2: Core Hybrid Logic
- [x] **Red Phase**: Create test for `process_hybrid_analysis` in `services/composite.py`
- [x] **Green Phase**: Implement `process_hybrid_analysis` (orchestrating both Matrix and Penta calculations)
- [x] **Refactor**: Optimize batch geocoding and loop efficiency
- [x] Task: Conductor - User Manual Verification 'Phase 2: Core Hybrid Logic' (Protocol in workflow.md)

## Phase 3: API Integration & Verification
- [x] **Red Phase**: Create integration test for `POST /analyze/maia-penta`
- [x] **Green Phase**: Implement the endpoint in `routers/composite.py`
- [x] **Verify**: Ensure geocoding bypass and verbosity flags handle all edge cases
- [x] Task: Conductor - User Manual Verification 'Phase 3: API Integration & Verification' (Protocol in workflow.md)

## Phase 4: 10x Optimization (Tier 1 & 2)
- [x] **Provenance**: Implement `meta` field (Engine, Ephemeris).
- [x] **Precision**: Implement exact planetary `position` (degrees).
- [x] **Variables**: Implement Primary Health System `variables` (PRL/DRR).
- [x] **Global Cycle**: Implement `lunar_context` (Phase).
- [x] **Validation**: Implement strict input validation for participants.
