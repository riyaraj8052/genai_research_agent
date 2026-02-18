# Databricks notebook source
# MAGIC %md
# MAGIC ####1. Install necessory packages

# COMMAND ----------

# MAGIC %pip install langgraph==0.5.3 databricks-langchain databricks-agents mlflow-skinny[databricks]
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv()

%load_ext autoreload
%autoreload 2

# COMMAND ----------

# MAGIC %md
# MAGIC ####2. Load, compile and display agent graph

# COMMAND ----------

from A03_scoping_agent import scope_agent_builder
from A04_utils import show_app_graph
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
lg_agent = scope_agent_builder.compile(checkpointer=checkpointer)
show_app_graph(lg_agent)

# COMMAND ----------

# MAGIC %md
# MAGIC 3.1 Scenario 1 - Most likely no clerification needed

# COMMAND ----------

import uuid
import mlflow
from langchain_core.messages import HumanMessage

query = "I want to research the best coffee shops in San Francisco."
thread = {"configurable": {"thread_id": uuid.uuid4()}}

with mlflow.start_span(name="Scoping Agent") as span:
    span.set_inputs({"User Query": query})
    result = lg_agent.invoke({"messages": [HumanMessage(content=query)]}, config=thread)
    span.set_outputs({"Agent Status": "Success",
                      "Confirmation": result["messages"][-1].content,
                      "Research Brief": result["research_brief"]})
    

# COMMAND ----------

# MAGIC %md
# MAGIC 3.2 Scenario 2 - Most likely a clerification is needed

# COMMAND ----------

import uuid
import mlflow
from langchain_core.messages import HumanMessage

query = "I want to compare Spark performance in Hadoop and Databricks."
thread = {"configurable": {"thread_id": uuid.uuid4()}}

with mlflow.start_span(name="Scoping Agent") as span:
    span.set_inputs({"User Query": query})
    result = lg_agent.invoke({"messages": [HumanMessage(content=query)]}, config=thread)
    span.set_outputs({"Agent Status": "Success",
                      "Question": result["messages"][-1].content,
                      "Research Brief": result.get("research_brief",[])})