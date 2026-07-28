from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

LLM = ChatGroq(model="openai/gpt-oss-120b", temperature=0.7)

class chatbotstate(TypedDict):
    
    messages: Annotated[list[BaseMessage], add_messages]
    
def chat_node(state: chatbotstate):
    chatmessages = state["messages"]
    response = LLM.invoke(chatmessages)
    return {'messages': [response]}
    
graph = StateGraph(chatbotstate)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

checkpointer = InMemorySaver()

chatbot = graph.compile(checkpointer=checkpointer)

