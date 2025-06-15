# Understanding LangChain Errors - A Comprehensive Guide

## 🔍 How to Read LangChain Errors

### 1. **Deprecation Warnings**
These are informational - your code still works but uses older patterns:

```
LangChainDeprecationWarning: The method `Chain.run` was deprecated in langchain 0.1.0...
```

**What it means:**
- LangChain is evolving and some methods are being replaced
- `.run()` → `.invoke()` (new standard)
- `AgentExecutor` → `LangGraph` (future direction)

**Action:** Update your code to use newer methods, but old ones still work for now.

### 2. **Missing Input Keys Errors**
```
ValueError: Missing some input keys: {'input'}
```

**What it means:**
- The agent/chain expects data in a specific dictionary format
- You're passing a string when it wants `{"input": "your string"}`

**Common patterns:**
```python
# OLD (causes error)
agent.run("Do something")

# NEW (correct)
agent.invoke({"input": "Do something"})
```

### 3. **Tool Errors**
```
Error: Missing some input keys: {'field'}
```

**What it means:**
- Tool descriptions contain JSON examples that confuse the parser
- Agent thinks `'field'` (with quotes) is a required parameter

## 📊 Error Analysis Workflow

### Step 1: Identify Error Type
1. **Import Error** → Missing package
2. **ValueError** → Wrong input format
3. **KeyError** → Missing expected data
4. **AttributeError** → Method doesn't exist

### Step 2: Read the Stack Trace
```
File "debug_tools.py", line 102, in <module>
    result = agent.run(query)  ← Your code
    ...
File "chains/base.py", line 287, in _validate_inputs
    raise ValueError(f"Missing some input keys: {missing_keys}")  ← Where it failed
```

### Step 3: Check Common Causes
- Wrong input format (string vs dict)
- Deprecated methods
- Tool description issues
- Memory/context problems

## 🆚 LangEntiChain vs AgenticSeek Comparison

### Architecture Differences

| Feature | LangEntiChain | AgenticSeek |
|---------|---------------|-------------|
| **Routing** | Simple keyword-based | ML-based with DistilBERT |
| **Agents** | Fixed specialist agents | Dynamic tool selection |
| **Memory** | ConversationBufferMemory | Custom context management |
| **Tools** | Direct function wrapping | Tool manifests/descriptions |
| **UI** | Streamlit | Custom web interface |

### Code Organization

**LangEntiChain:**
```
langentichain/
├── agents/          # Agent implementations
├── routing/         # Simple router
├── tools/           # Tool functions
└── main.py          # Entry point
```

**AgenticSeek:**
```
agenticSeek/
├── server/          # FastAPI backend
├── ui/              # React frontend  
├── tools/           # Tool manifests
└── router/          # ML router
```

### Key Technical Differences

1. **Tool Definition**
   - **LangEntiChain**: Direct Python functions wrapped with Tool()
   - **AgenticSeek**: JSON manifests with schemas

2. **Routing Logic**
   - **LangEntiChain**: Keyword matching for simplicity
   - **AgenticSeek**: Embeddings + few-shot learning

3. **Error Handling**
   - **LangEntiChain**: Try/catch with custom handlers
   - **AgenticSeek**: Structured error responses

4. **LLM Integration**
   - **LangEntiChain**: Custom wrapper for Ollama/LM Studio
   - **AgenticSeek**: Provider abstraction layer

## 🛠️ Debugging Tools

### 1. Enable Verbose Mode
```ini
[AGENT]
verbose = true
```

### 2. Add Debug Prints
```python
# In your agent code
print(f"Input type: {type(input)}")
print(f"Input value: {input}")
```

### 3. Use the Debug Script
```bash
python debug_tools.py
```

### 4. Check Tool Calls
```python
# See what the agent is trying to do
agent.callbacks = [MyDebugCallback()]
```

## 📋 Common Fixes

### Fix 1: Update to New API
```python
# Replace all .run() calls
- result = agent.run(query)
+ result = agent.invoke({"input": query})
+ output = result.get('output', result)
```

### Fix 2: Clear Tool Descriptions
```python
# Remove JSON examples from descriptions
- description="Fill form: {'field': 'value'}"
+ description="Fill form fields. Input should be JSON format"
```

### Fix 3: Handle Memory Properly
```python
# Use the right memory key
memory = ConversationBufferMemory(
    memory_key="chat_history",  # Must match prompt template
    return_messages=True
)
```

### Fix 4: Validate Inputs
```python
# Always validate before calling
if not isinstance(query, dict):
    query = {"input": query}
```

## 🎯 Quick Error Reference

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| `Missing input keys` | Wrong format | Use `{"input": value}` |
| `No tool named X` | Tool not found | Check tool name spelling |
| `'field'` error | Bad description | Update tool descriptions |
| `run() deprecated` | Old API | Use `invoke()` instead |
| `Memory error` | Wrong key | Check memory_key matches |

## 🔄 Migration Tips

If moving from AgenticSeek patterns:
1. Replace manifest-based tools with Python functions
2. Simplify routing (no ML needed for basic use)
3. Use LangChain's built-in memory
4. Adapt error handling patterns

Remember: LangChain is evolving rapidly. What works today might have a better way tomorrow!
