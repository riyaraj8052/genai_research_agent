# Databricks notebook source
# MAGIC %md
# MAGIC ####1. Set the notebook/job parameters

# COMMAND ----------

dbutils.widgets.text("target_catalog", "rsa_uat", "Set the target system catalog name")
dbutils.widgets.text("target_database", "rsa_db", "Set the target system database name")
dbutils.widgets.text("model_name", "research_system_agent", "Set the current agent/model name")
dbutils.widgets.text("model_version", "1", "Set the current agent/model version")

target_catalog = dbutils.widgets.get("target_catalog")
target_database = dbutils.widgets.get("target_database")

model_name = dbutils.widgets.get("model_name")
model_version = dbutils.widgets.get("model_version")
model_payload_table = model_name + "_payload"

# COMMAND ----------

# MAGIC %md
# MAGIC ####2. Delete deployment

# COMMAND ----------

from databricks.agents import delete_deployment
from mlflow import MlflowClient

UC_MODEL_NAME = f"{target_catalog}.{target_database}.{model_name}"
UC_MODEL_PAYLOAD_TABLE = f"{target_catalog}.{target_database}.{model_payload_table}"

delete_deployment(model_name=UC_MODEL_NAME, model_version=model_version)
spark.sql(f"DROP TABLE IF EXISTS {UC_MODEL_PAYLOAD_TABLE}")

client = MlflowClient()
client.delete_model_version(name=UC_MODEL_NAME, 
                            version=model_version)
client.delete_registered_model(name=UC_MODEL_NAME)