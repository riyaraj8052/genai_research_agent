"""Configuration file.

This module provides configurable values at the time of deployment.
"""

import mlflow

# ===== MODEL CONFIGS =====

model_config = mlflow.models.ModelConfig(development_config=f"../configs/model_configs.yml")