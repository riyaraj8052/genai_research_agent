# Databricks notebook source
# MAGIC %md
# MAGIC ####Comment this section: 
# MAGIC This section is for manual testing\
# MAGIC Comment this section when using this notebook for a deployment job

# COMMAND ----------

# Comment this code for a deployment job
# Dependencies for DBX 17.3 ML Cluster with databricks-connect==17.0.9

%pip install langgraph==0.5.3 databricks-langchain==0.8.2 databricks-agents==1.8.1 mlflow-skinny[databricks]==3.5.1 uv==0.9.7 tavily-python==0.7.12

dbutils.library.restartPython()

# COMMAND ----------

# Comment this code for a deployment job

import os
from A00_configs import model_config

tavily_api_key = dbutils.secrets.get(
    scope=model_config.get("databricks_secret_scope_name"), 
    key="tavily-api-key")
os.environ["TAVILY_API_KEY"] = tavily_api_key

# COMMAND ----------

# MAGIC %md
# MAGIC ####1. Setup Notebook Parameters

# COMMAND ----------

# Setup the parameter widgets for a deployment job

# dbutils.widgets.text("target_catalog", "rsa_dev", "Set the target system catalog name")
# dbutils.widgets.text("target_database", "rsa_db", "Set the target system database name")
# dbutils.widgets.text("model_name", "research_system_agent", "Set the current agent/model name")
# dbutils.widgets.text("model_endpoint_name", "research_agent_endpoint_dev", "Set the model endpoint name")

# COMMAND ----------

# Get the parameters from the widgets for a deployment job

target_catalog = "rsa_dev" # dbutils.widgets.get("target_catalog")
target_database = "rsa_db" # dbutils.widgets.get("target_database")

model_name = "research_system_agent" # dbutils.widgets.get("model_name")
model_endpoint_name = "research_agent_endpoint_dev" # dbutils.widgets.get("model_endpoint_name")
model_payload_table = model_name + "_payload"

# COMMAND ----------

# MAGIC %md
# MAGIC ####2. Log the model

# COMMAND ----------

import mlflow
from mlflow.models.resources import DatabricksServingEndpoint
from pkg_resources import get_distribution
from uuid import uuid4
from mlflow.types.responses import ResponsesAgentRequest
from A00_configs import model_config
from A09_research_system import AGENT

resources = [DatabricksServingEndpoint(endpoint_name=model_config.get("research_model_serving_endpoint"))]

thread_id = str(uuid4())
input_example = ResponsesAgentRequest(
  input=[{"role": "user", "content": "I want to compare Apache Spark on Databricks and Cloudera."}],
  context={"conversation_id": thread_id},
  custom_inputs={"recursion_limit": 50}
)

logged_agent_info = mlflow.pyfunc.log_model(
    name=model_name,
    python_model="A09_research_system.py",
    code_paths=["A00_configs.py", "A01_prompts.py", "A02_scoping_agent_schema.py", 
                "A03_scoping_agent.py", "A04_utils.py", "A05_research_agent_schema.py", 
                "A06_research_agent.py", "A07_supervisor_agent_schema.py", "A08_supervisor_agent.py",],
    input_example=input_example,
    resources=resources,
    model_config="../configs/model_configs.yml",
    pip_requirements=[
        f"databricks-connect=={get_distribution('databricks-connect').version}",
        f"mlflow=={get_distribution('mlflow').version}",
        f"databricks-langchain=={get_distribution('databricks-langchain').version}",
        f"databricks-agents=={get_distribution('databricks-agents').version}",
        f"langgraph=={get_distribution('langgraph').version}",
        f"uv=={get_distribution('uv').version}",
        f"tavily-python=={get_distribution('tavily-python').version}"    
    ]
)

# COMMAND ----------

# MAGIC %md
# MAGIC ####3. Register the model

# COMMAND ----------

mlflow.set_registry_uri("databricks-uc")

UC_MODEL_NAME = f"{target_catalog}.{target_database}.{model_name}"

uc_registered_model_info = mlflow.register_model(
    model_uri=logged_agent_info.model_uri, 
    name=UC_MODEL_NAME
)

# COMMAND ----------

# MAGIC %md
# MAGIC ####4. Deploy serving endpoint

# COMMAND ----------

from databricks import agents

deployment = agents.deploy(model_name=UC_MODEL_NAME, 
                           model_version=uc_registered_model_info.version, 
                           scale_to_zero_enabled=True,
                           endpoint_name=model_endpoint_name,
                           deploy_feedback_model=False,
                           environment_vars={"TAVILY_API_KEY": "{{secrets/rsa-project-secrets/tavily-api-key}}",
                                             "MLFLOW_HTTP_REQUEST_TIMEOUT": "600"})

# COMMAND ----------

# MAGIC %md
# MAGIC ####5. Delete Deployment

# COMMAND ----------

# Comment this code for a deployment job

agents.delete_deployment(model_name=UC_MODEL_NAME, 
                         model_version=uc_registered_model_info.version)

UC_MODEL_PAYLOAD_TABLE = f"{target_catalog}.{target_database}.{model_payload_table}"
spark.sql(f"DROP TABLE IF EXISTS {UC_MODEL_PAYLOAD_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ####6. Cleanup registered model

# COMMAND ----------

# Comment this code for deployment

from mlflow import MlflowClient

client = MlflowClient()
client.delete_model_version(name=UC_MODEL_NAME, 
                            version=uc_registered_model_info.version)
client.delete_registered_model(name=UC_MODEL_NAME)