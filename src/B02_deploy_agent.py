# Databricks notebook source
# MAGIC %md
# MAGIC ####1. Set the notebook/job parameters

# COMMAND ----------

dbutils.widgets.text("source_catalog", "rsa_dev", "Set the source system catalog name")
dbutils.widgets.text("source_database", "rsa_db", "Set the source system database name")
dbutils.widgets.text("target_catalog", "rsa_dev", "Set the target system catalog name")
dbutils.widgets.text("target_database", "rsa_db", "Set the target system database name")
dbutils.widgets.text("model_name", "research_system_agent", "Set the current agent/model name")
dbutils.widgets.text("model_version", "1", "Set the current agent/model version")
dbutils.widgets.text("model_endpoint_name", "rsa_endpoint_uat", "Set the model endpoint name")

source_catalog = dbutils.widgets.get("source_catalog")
source_database = dbutils.widgets.get("source_database")
target_catalog = dbutils.widgets.get("target_catalog")
target_database = dbutils.widgets.get("target_database")

model_name = dbutils.widgets.get("model_name")
model_version = dbutils.widgets.get("model_version")
model_endpoint_name = dbutils.widgets.get("model_endpoint_name")

# COMMAND ----------

# MAGIC %md
# MAGIC ####2. Register the model to the target database from a source database

# COMMAND ----------

import mlflow
from mlflow import MlflowClient
mlflow.set_registry_uri("databricks-uc")
client = MlflowClient()

src_model_name = f"{source_catalog}.{source_database}.{model_name}"
src_model_version = model_version
src_model_uri = f"models:/{src_model_name}/{src_model_version}"
dst_model_name = f"{target_catalog}.{target_database}.{model_name}"

copied_model_info = client.copy_model_version(src_model_uri, dst_model_name)

# COMMAND ----------

# MAGIC %md
# MAGIC ####3. Deploy the model to an endpoint

# COMMAND ----------

from databricks import agents
from A00_configs import model_config

UC_MODEL_NAME = f"{target_catalog}.{target_database}.{model_name}"
secret_scope_name = model_config.get("databricks_secret_scope_name")

deployment = agents.deploy(model_name=UC_MODEL_NAME, 
                           model_version=copied_model_info.version, 
                           scale_to_zero_enabled=True,
                           endpoint_name=model_endpoint_name,
                           deploy_feedback_model=False,
                           environment_vars={"TAVILY_API_KEY": f"{{{{secrets/{secret_scope_name}/tavily-api-key}}}}",
                                             "MLFLOW_HTTP_REQUEST_TIMEOUT": "600"})