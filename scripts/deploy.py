import argparse
import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deploy-script")

def deploy(env="dev"):
    """Deploy the Modal app with a specific environment."""
    logger.info(f"Deploying portfolio-app to environment: {env}")
    
    # Set the environment variable for the Modal app to pick up
    env_vars = {"APP_ENV": env}
    
    try:
        # Using 'modal deploy' command
        subprocess.run(
            ["modal", "deploy", "src/app/main.py"],
            env={**os.environ, **env_vars},
            check=True
        )
        logger.info(f"Successfully deployed to {env}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import os
    parser = argparse.ArgumentParser(description="Production Deploy Script")
    parser.add_argument("--env", default="dev", choices=["dev", "staging", "prod"], help="Deployment environment")
    args = parser.parse_args()
    deploy(args.env)
