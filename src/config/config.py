import os
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class AppConfig:
    model_name: str
    tensor_parallel: int
    gpu_type: str
    gpu_count: int
    dtype: str
    enable_prefix_caching: bool
    enable_chunked_prefill: bool
    max_model_len: int
    max_num_batched_tokens: int
    max_num_seqs: int
    concurrent_inputs: int
    min_containers: int
    max_containers: int
    fast_boot: bool
    mm_max_pixels: int
    env: str

def load_config() -> AppConfig:
    env = os.environ.get("APP_ENV", "dev").lower()
    
    # Default configuration (Dev)
    config_data: Dict[str, Any] = {
        "model_name": "Qwen/Qwen3-VL-4B-Instruct",
        "tensor_parallel": 1,
        "gpu_type": "H100",
        "gpu_count": 1,
        "dtype": "bfloat16",
        "enable_prefix_caching": True,
        "enable_chunked_prefill": True,
        "max_model_len": 8192,
        "max_num_batched_tokens": 4096,
        "max_num_seqs": 32,
        "concurrent_inputs": 64,
        "min_containers": 1,
        "max_containers": 1,
        "fast_boot": True,
        "mm_max_pixels": 512 * 28 * 28,
        "env": env
    }

    # Environment specific overrides
    if env == "prod":
        config_data.update({
            "min_containers": 2,
            "max_containers": 10,
            "concurrent_inputs": 128,
            "fast_boot": False, # Better throughput in prod
        })
    elif env == "staging":
        config_data.update({
            "min_containers": 1,
            "max_containers": 2,
        })

    # Allow environment variable overrides for any config key
    for key in config_data.keys():
        env_val = os.environ.get(key.upper())
        if env_val is not None:
            # Basic type casting
            val = config_data[key]
            if isinstance(val, bool):
                config_data[key] = env_val.lower() == "true"
            elif isinstance(val, int):
                config_data[key] = int(env_val)
            else:
                config_data[key] = env_val

    return AppConfig(**config_data)
