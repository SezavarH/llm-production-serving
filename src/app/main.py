import os
import subprocess
import logging
import modal
from src.config.config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("inference-app")

# vLLM image definition
vllm_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12"
    )
    .entrypoint([])
    .uv_pip_install("vllm==0.21.0", "qwen-vl-utils==0.0.14")
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})
)

app = modal.App("portfolio-inference-app")

# Persistent caches
hf_cache = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("vllm-cache", create_if_missing=True)

@app.function(
    image=vllm_image,
    gpu="H100:1", # Default, will be overridden by config in production deploy if needed
    scaledown_window=600,
    min_containers=1,
    max_containers=1,
    timeout=900,
    volumes={
        "/root/.cache/huggingface": hf_cache,
        "/root/.cache/vllm": vllm_cache,
    },
    secrets=[modal.Secret.from_name("huggingface", required_keys=["HF_TOKEN"])],
)
@modal.concurrent(max_inputs=64)
@modal.web_server(port=8000, startup_timeout=900)
def serve():
    """Start vLLM inside the Modal container."""
    config = load_config()
    
    cmd = [
        "vllm",
        "serve",
        config.model_name,
        "--served-model-name",
        config.model_name,
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--tensor-parallel-size",
        str(config.tensor_parallel),
        "--dtype",
        config.dtype,
        "--max-model-len",
        str(config.max_model_len),
        "--max-num-batched-tokens",
        str(config.max_num_batched_tokens),
        "--max-num-seqs",
        str(config.max_num_seqs),
        "--gpu-memory-utilization",
        "0.90",
        "--uvicorn-log-level=warning",
        "--limit-mm-per-prompt",
        '{"image": 1, "video": 0}',
        "--mm-processor-kwargs",
        f'{{"min_pixels": 784, "max_pixels": {config.mm_max_pixels}, "fps": 1}}',
    ]

    if config.fast_boot:
        cmd += ["--enforce-eager"]
    else:
        cmd += ["--no-enforce-eager"]

    if config.enable_prefix_caching:
        cmd += ["--enable-prefix-caching"]

    if config.enable_chunked_prefill:
        cmd += ["--enable-chunked-prefill"]

    logger.info(f"Starting vLLM with config env={config.env}. Command: {' '.join(cmd)}")
    
    try:
        subprocess.Popen(cmd)
    except Exception as e:
        logger.error(f"Failed to start vLLM: {e}")
        raise e
