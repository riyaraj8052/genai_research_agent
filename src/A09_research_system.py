"""
Full Multi-Agent Research System

This module integrates all components of the research system:
- User clarification and scoping
- Research brief generation  
- Multi-agent research coordination
- Final report generation

The system orchestrates the complete research workflow from initial user
input through final report delivery.
"""

import mlflow
from mlflow.entities import SpanType
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from typing import Any

from A01_prompts import final_report_generation_prompt
from A02_scoping_agent_schema import AgentState, AgentInputState
from A03_scoping_agent import clarify_with_user, write_research_brief
from A08_supervisor_agent import supervisor_agent
from A04_utils import model_config, get_today_str
from databricks_langchain import ChatDatabricks
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import ResponsesAgentRequest, ResponsesAgentResponse
from langgraph.checkpoint.memory import InMemorySaver

# ===== Config =====

LLM_ENDPOINT_NAME = model_config.get("research_model_serving_endpoint")
writer_model = ChatDatabricks(endpoint=LLM_ENDPOINT_NAME)

# ===== FINAL REPORT GENERATION =====

def final_report_generation(state: AgentState):
    """
    Final report generation node.
    
    Synthesizes all research findings into a comprehensive final report
    """
    
    notes = state.get("notes", [])
    
    findings = "\n".join(notes)

    final_report_prompt = final_report_generation_prompt.format(
        research_brief=state.get("research_brief", ""),
        findings=findings,
        date=get_today_str()
    )
    
    final_report = writer_model.invoke([HumanMessage(content=final_report_prompt)])
    
    return {
        "final_report": final_report.content, 
        "messages": [AIMessage("Here is the final report: " + final_report.content)],
    }

# ===== DATABRICKS WRAPPER =====
class LangGraphResponsesAgent(ResponsesAgent):
    def __init__(self, agent):
        # Reference your existing agent
        self.agent = agent

    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        # Convert incoming messages to your agent's format
        cc_messages = self.prep_msgs_for_cc_llm([i.model_dump() for i in request.input])
        # Call your existing agent (non-streaming)
        configs = {"configurable": {"thread_id": request.context.conversation_id, 
                                    "recursion_limit": request.custom_inputs.get("recursion_limit", 50)}}
        agent_response = self.agent.invoke({"messages": cc_messages}, config=configs)
        last_message = agent_response["messages"][-1]
        output_item = self.create_text_output_item(text=last_message.content,
                                                   id=last_message.id or str(uuid4()))

        # Return the response
        return ResponsesAgentResponse(output=[output_item], 
                                      custom_outputs={"final_report": agent_response.get("final_report", "")}
                                      )
    

# ===== GRAPH CONSTRUCTION =====
# Build the overall workflow
research_system_builder = StateGraph(AgentState, input_schema=AgentInputState)

# Add workflow nodes
research_system_builder.add_node("clarify_with_user", clarify_with_user)
research_system_builder.add_node("write_research_brief", write_research_brief)
research_system_builder.add_node("research_coordinator_agent", supervisor_agent)
research_system_builder.add_node("final_report_generation", final_report_generation)

# Add workflow edges
research_system_builder.add_edge(START, "clarify_with_user")
research_system_builder.add_edge("write_research_brief", "research_coordinator_agent")
research_system_builder.add_edge("research_coordinator_agent", "final_report_generation")
research_system_builder.add_edge("final_report_generation", END)

# Compile the full workflow
mlflow.langchain.autolog()
checkpointer = InMemorySaver()
lg_research_system_agent = research_system_builder.compile(checkpointer=checkpointer)
AGENT = LangGraphResponsesAgent(lg_research_system_agent)
mlflow.models.set_model(AGENT)


