# Production Refactor Report

## 🛠 Changes Made

### 1. Structural Overhaul
Moved from a flat file structure to a professional modular layout:
- `src/app/`: Core logic.
- `src/config/`: Centralized configuration.
- `scripts/`: Automation for deployment.
- `tests/`: Placeholder for validation.

### 2. Configuration Management
**Before**: Hardcoded constants patched via string replacement in `run_experiment.py`.
**After**: A dedicated `AppConfig` dataclass with environment-based overrides (`dev`, `staging`, `prod`). This allows the same codebase to behave differently across environments without modifying source code.

### 3. Security Improvements
- **Secret Handling**: Verified that `modal.Secret` is used for `HF_TOKEN`, ensuring no keys are leaked in the repository.
- **Input Validation**: Configuration is now typed and validated via dataclasses.

### 4. Production Readiness
- **Logging**: Replaced `print` statements with Python's `logging` module for better observability and log level control.
- **Error Handling**: Added try-except blocks around critical startup paths (vLLM process spawning).
- **Scaling**: Configured production environment to support multiple replicas and disabled `fast_boot` in favor of higher throughput (compiled mode).

## 📊 Experimental Results & Insights

Based on baseline experiments conducted during the development phase, the following performance trends were observed. These results informed the production configuration choices:

### Performance Benchmarks (Text Mode, H100)

| Experiment | Users | Replicas | Config | p95 TTFT | p95 ITL | Throughput | Score |
|---|---|---|---|---|---|---|---|
| **Baseline** | 50 | 1 | Eager, Cache ON | 790 ms | 17.3 ms | 1,433 ch/s | 5.2M |
| **Saturation** | 100 | 1 | Eager, Cache ON | 3,605 ms | 21.3 ms | 1,459 ch/s | 1.9M |
| **No Cache** | 50 | 1 | Eager, Cache OFF | 551 ms | 19.6 ms | 1,454 ch/s | 6.7M |
| **Boss Fight** | 600 | 8 | Compiled, Cache OFF | 1,327 ms | 5.9 ms | High | 174M |

### Key Engineering Insights
- **Saturation Point**: A single H100 GPU saturates at approximately 50–75 concurrent users. Beyond this, TTFT grows super-linearly, causing the overall score to plummet despite stable throughput.
- **Prefix Caching Paradox**: For short system prompts (~40 tokens), disabling prefix caching actually improved performance. This suggests that the overhead of managing the cache outweighs the computation savings for very small prefixes.
- **Scaling Efficiency**: Doubling GPU count (e.g., moving to 8 replicas) significantly increases total throughput but can decrease the efficiency score if the user load doesn't scale proportionally or if error rates increase.
- **Throughput vs. Latency**: Switching from "Fast Boot" (Eager mode) to Compiled mode dramatically reduces Inter-Token Latency (ITL), which is critical for the "feel" of a production AI tutor.

## ⚖️ Key Decisions

- **Config Over Patches**: I eliminated the `patch_modal_app` logic from the original `run_experiment.py`. String replacement in source code is fragile and insecure. Environment variables and a config loader are the industry standard.
- **Modal for Deployment**: Kept Modal as the infrastructure layer due to its excellent GPU orchestration, but wrapped it in a deployment script to standardize the process.
- **Eager vs Compiled**: In `dev`, we prioritize `enforce-eager` for fast startup. In `prod`, we allow vLLM to optimize for throughput.

## ⚠️ Known Limitations

- **Unit Testing**: While the directory structure exists, full end-to-end tests require active GPU resources on Modal.
- **Cold Starts**: Modal functions have a cold start period; `min_containers` in `prod` config is intended to mitigate this.

## 🚀 Deployment Flow
`User` $\rightarrow$ `scripts/deploy.py` $\rightarrow$ `Modal Cloud` $\rightarrow$ `vLLM Server`
