# Databricks notebook source
# MAGIC %pip install langgraph databricks-langchain databricks-agents mlflow-skinny[databricks] uv tavily-python grandalf 
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

from A06_research_agent import research_agent_builder
from A04_utils import show_app_graph

lg_agent = research_agent_builder.compile()
show_app_graph(lg_agent)

# COMMAND ----------

import mlflow
from langchain_core.messages import HumanMessage

research_brief = """I want to research the best coffee shops in San Francisco, focusing on key attributes such as coffee quality, ambiance, customer service, and unique offerings. Additionally, I would like to consider the diversity of drink options and food pairings available. While I am not specifying a budget, I am open to reviewing a range of price points. I would prefer to gather information from official coffee shop websites and reputable review platforms to ensure the accuracy and reliability of the recommendations."""

with mlflow.start_span(name="Research Agent") as span:
  span.set_inputs({"Research Brief": research_brief})
  result = lg_agent.invoke({"researcher_messages": [HumanMessage(content=research_brief)]})
  span.set_outputs({"Agent Status": "success",
                    "Final Message": result["researcher_messages"][-1].content,
                    "Compressed Research": result["compressed_research"] })