# 🏃‍♂️ Getting Started (No Docker)

### From the folder:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

# 🐳 Getting Started (With Docker)

```bash
docker build -t langchain-agentic-chat .
docker run -p 8501:8501 langchain-agentic-chat
```

-------------------------------------------------------------------------



>> `python -m venv my_langentichain_env`

>> After that you can:

>> `.\my_langentichain_env\Scripts\activate` (DON'T USE .BAT)

>> which will open your distinct environment. Here you can do all the things you want, e.g., install your packages using pip etc. 

>> **After you completed setting up the environment, you can freeze the environment and create a requirements file:**

>> `pip freeze > requirements.txt`

>> to be able to reconstruct the environment if needed. This way all the overhead that may be needed (setting a PATH etc.) will be handled by pyenv.

>> If you want to work on different projects, just activate the environment you need and off you go!

>> Note that you can make pyenv activate the virtualenv when you cd the folder in your terminal by putting its name into your .python-version file as well.


-----------------------------------------------------------

Here's a comprehensive test prompt that exercises all the key features:

"Search the web for the current price of Bitcoin and Ethereum in USD, along with their 24-hour percentage changes. Then read the config.ini file in the current directory to identify which LLM provider I'm using. Finally, create a new file called 'crypto_report.txt' that contains: 1) Current date and time, 2) The cryptocurrency prices and changes you found, 3) The LLM provider from the config file, and 4) A brief 2-sentence analysis of whether crypto prices are trending up or down today. Format the report with clear headers for each section."

This prompt will test:

Web search: Looking up real-time crypto prices
File reading: Reading the config.ini file
File writing: Creating a new report file
Agentic planning: The system should break this into multiple tasks (web agent for search, file agent for reading/writing)
Data synthesis: Combining information from multiple sources

You can shorten it if needed, but this should trigger all the major capabilities of both AgenticSeek and any LangChain-based agentic system. The prompt is complex enough to require planning but simple enough to complete successfully.