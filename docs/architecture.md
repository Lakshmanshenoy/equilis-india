# Architecture

## Layers

- Skill layer: reusable analysis instructions
- Prompt modules: task-specific analysis paths
- Templates: output formatting
- Core pipeline: validation and orchestration
- Host adapters: editor or agent integration

## Contract

The host adapter should never reimplement the analysis logic.
