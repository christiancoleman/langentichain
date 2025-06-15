from langchain.agents import initialize_agent, AgentType, Tool
from langchain.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory
from tools.salesforce import search_salesforce
from tools.web_browser import browse_web

tools = [
	Tool(name="SalesforceSearch", func=search_salesforce, description="Search Salesforce for data"),
	Tool(name="WebBrowser", func=browse_web, description="Perform a basic web browsing query")
]

llm = ChatOllama(model="deepseek-coder:33b")  # adjust to a local model you can run

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
	tools=tools,
	llm=llm,
	agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
	memory=memory,
	verbose=True
)

def run_agent(user_input):
	return agent.run(user_input)
