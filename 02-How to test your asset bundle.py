# Databricks notebook source
# MAGIC %md
# MAGIC You can use the terminal to test your databricks asset bundle.
# MAGIC 1. Do the following to enable terminal in your workspace.
# MAGIC     1. Manage Accounts -> Settings -> Feature Enablement -> Web Terminal=On
# MAGIC     2. Workspace -> Settings -> Compute -> Web Terminal=On
# MAGIC     3. Refresh your workspace UI
# MAGIC
# MAGIC 2. Do the following to start the terminal
# MAGIC     1. Connect this notebook to a running cluster
# MAGIC     2. Start the terminal using the button at the right-bottom
# MAGIC     3. Use cd command to change to the directorey where databricks.yml file is stored

# COMMAND ----------

# MAGIC %md
# MAGIC Use the following commands to test your bundle from the terminal
# MAGIC 1. Use the following command to validate your asset bundle\
# MAGIC     ```databricks bundle validate```
# MAGIC
# MAGIC 2. Use the following command to deploy your assets\
# MAGIC     ```databricks bundle deploy -t uat```
# MAGIC
# MAGIC 3. Use the following command to run the agent deployment job\
# MAGIC     ```databricks bundle run -t uat deploy_agent```
# MAGIC
# MAGIC 4. Use the following command to run the cleanup\
# MAGIC     ```databricks bundle run -t uat delete_deployment```
# MAGIC
# MAGIC 5. Use the following command to remove your assets\
# MAGIC     ```databricks bundle destroy -t uat --auto-approve```
# MAGIC