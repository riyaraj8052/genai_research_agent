# Databricks notebook source
# MAGIC %pip install langgraph==0.5.3 databricks-langchain databricks-agents mlflow-skinny[databricks] uv tavily-python databricks-sdk grandalf 
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

from dotenv import load_dotenv
load_dotenv()

%load_ext autoreload
%autoreload 2

# COMMAND ----------

import os
from A00_configs import model_config

tavily_api_key = dbutils.secrets.get(
    scope=model_config.get("databricks_secret_scope_name"), 
    key="tavily-api-key")
os.environ["TAVILY_API_KEY"] = tavily_api_key

# COMMAND ----------

# MAGIC %md
# MAGIC ####1. Load , compile and display agent graph

# COMMAND ----------

from A09_research_system import lg_research_system_agent
from A04_utils import show_app_graph

show_app_graph(lg_research_system_agent)

# COMMAND ----------

# MAGIC %md
# MAGIC ####2. Test langgraph agent

# COMMAND ----------

import mlflow
from langchain_core.messages import HumanMessage
import uuid

query = """I want to research the best coffee shops in San Francisco."""
configs = {"configurable": {"thread_id": uuid.uuid4(), "recursion_limit": 50}}

mlflow.langchain.autolog()
with mlflow.start_span(name="Deep Research System") as span:
  span.set_inputs({"User Query": query})
  result = lg_research_system_agent.invoke({"messages": [HumanMessage(content=query)]}, config=configs)
  span.set_outputs({"Agent Status": "success",
                    "Result": result})

# COMMAND ----------

# MAGIC %md
# MAGIC ####3. Test Databricks Responses Agent

# COMMAND ----------

import mlflow
from mlflow.types.responses import ResponsesAgentRequest
from A09_research_system import AGENT
from uuid import uuid4

thread_id = str(uuid4())
request = ResponsesAgentRequest(
  input=[{"role": "user", 
          "content": "I want to list top 3 coffee shops in San Francisco based on coffee quality."}],
  context={"conversation_id": thread_id},
  custom_inputs={"recursion_limit": 50}
  )

mlflow.langchain.autolog()
with mlflow.start_span(name="Deep Research Agent") as span:
  span.set_inputs({"Request": request})
  result = AGENT.predict(request)
  span.set_outputs({"Agent Status": "success",
                    "Response": result})