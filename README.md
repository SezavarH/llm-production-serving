# Inference App - Production Ready vLLM Serving

This application is a production-ready refactor of the InferTutor arena, designed to serve multimodal LLMs (specifically Qwen3-VL) using vLLM on Modal.

## 🏗 Architecture

- **`src/app/`**: Contains the core Modal application logic.
- **`src/config/`**: Environment-based configuration management.
- **`src/utils/`**: Shared helper functions.
- **`tests/`**: Unit and integration tests for the serving pipeline.
- **`scripts/`**: Deployment and management scripts.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Modal account and configured CLI (`modal setup`)
- HuggingFace token stored in Modal secrets as `huggingface`

### Installation
```bash
cd portfolio-app
pip install -r requirements.txt
```

### Running the App
The app is designed to be deployed to Modal for production serving.

**Development Deploy:**
```bash
python scripts/deploy.py --env dev
```

**Production Deploy:**
```bash
python scripts/deploy.py --env prod
```

## ⚙️ Configuration

The app uses environment-based configuration located in `src/config/config.py`. 

| Environment | Scaling | Performance Mode | Use Case |
|---|---|---|---|
| `dev` | 1 Replica | Fast Boot (Eager) | Testing & Iteration |
| `staging` | 1-2 Replicas | Mixed | Pre-prod Validation |
| `prod` | 2-10 Replicas | Optimized (Compiled) | End Users |

You can override any configuration via environment variables (e.g., `MODEL_NAME=... python scripts/deploy.py`).

## 🔒 Security & Best Practices

- **Secrets Management**: No API keys are hardcoded. We use `modal.Secret` to securely inject HF tokens.
- **Logging**: Structured logging implemented across the application.
- **Error Handling**: Wrapped subprocess calls and Modal function decorators for stability.
- **Resource Capping**: GPU memory utilization capped at 90% to prevent OOMs.
