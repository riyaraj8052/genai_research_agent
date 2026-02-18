# Databricks notebook source
# MAGIC %md
# MAGIC ####Start Terminal
# MAGIC You can use the terminal to test your databricks asset bundle.
# MAGIC 1. Do the following to enable terminal in your workspace.
# MAGIC     1. Manage Accounts -> Settings -> Feature Enablement -> Web Terminal=On
# MAGIC     2. Workspace -> Settings -> Compute -> Web Terminal=On
# MAGIC     3. Refresh your workspace UI
# MAGIC 2. Do the following to start the terminal
# MAGIC     1. Connect this notebook to a running cluster
# MAGIC     2. Start the terminal using the button at the right-bottom
# MAGIC     3. Use cd command to change to the directorey where databricks.yml file is stored
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ####Create Secrets 
# MAGIC You can create a databricks secret using the below steps
# MAGIC
# MAGIC 1. Create a secret scope (a collection of secrets) using below command\
# MAGIC     ```databricks secrets create-scope rsa-project-secrets```
# MAGIC
# MAGIC 2. Use the following command to add your secret key/value pairs\
# MAGIC     ```databricks secrets put-secret rsa-project-secrets tavily-api-key --string-value <your-tavily-api-key>```\
# MAGIC     ```databricks secrets put-secret rsa-project-secrets openai-api-key --string-value <your-openai-api-key>```
# MAGIC
# MAGIC 3. List secrets in the secret scope\
# MAGIC     ```databricks secrets list-secrets rsa-project-secrets```
# MAGIC
# MAGIC 4. Create an Open AI Model Serving Endpoint and define API key using secret\
# MAGIC     ```{{secrets/rsa-project-secrets/openai-api-key}}```
# MAGIC