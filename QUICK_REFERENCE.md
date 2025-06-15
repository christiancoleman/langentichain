# 🎯 LangChain Quick Reference Card

## Common Error Fixes

### Missing Input Keys
```python
# ❌ ERROR: Missing some input keys: {'input'}
result = agent.run(query)

# ✅ FIX:
result = agent.invoke({"input": query})
output = result.get('output', result)
```

### Tool Description Errors
```python
# ❌ ERROR: Missing some input keys: {'field'}
Tool(description="Fill form: {'field': 'value'}")

# ✅ FIX:
Tool(description="Fill form. Input should be JSON format")
```

### No Input Function Error
```python
# ❌ ERROR: Tool function takes 0 arguments
def extract_text():
    return "text"

# ✅ FIX:
def extract_text(dummy_input: str = ""):
    return "text"
```

## API Changes (Old → New)

| Old Method | New Method | Notes |
|------------|------------|-------|
| `agent.run(query)` | `agent.invoke({"input": query})` | Returns dict |
| `chain.run()` | `chain.invoke()` | Use .get('output') |
| `Chain()` | Use specific chain types | Or LangGraph |
| `verbose=True` in code | Set in config.ini | Cleaner setup |

## Tool Input Formats

### Browser Agent
```python
NavigateTo: "https://example.com"
ExtractText: ""  # Empty string
FillForm: '{"username": "john", "password": "pass"}'
Click: "Submit Button"
Screenshot: "page.png"  # or "" for auto
```

### File Agent
```python
ReadFile: "path/to/file.txt"
WriteFile: "output.txt|Content goes here"
ListFiles: "."  # or "/path/to/dir"
```

### Search Agent
```python
WebSearch: "your search query"
```

## Debugging Commands

```bash
# Test imports
python test_imports.py

# Check system
python system_check.py

# Debug tools
python debug_tools.py

# Diagnose errors
python diagnose_errors.py

# Compare with AgenticSeek
python compare_architectures.py
```

## Config Settings

```ini
[LLM]
provider = lm_studio      # or ollama
temperature = 0.7         # Higher = more creative
max_tokens = 4096        # Response length

[AGENT]
verbose = true           # See agent thinking
max_iterations = 1000    # Prevent infinite loops

[BROWSER]
headless = false         # Show browser window
```

## Memory Patterns

```python
# Buffer Memory (remembers everything)
memory = ConversationBufferMemory(
    memory_key="chat_history"
)

# Summary Memory (for long conversations)
memory = ConversationSummaryMemory(
    llm=llm,
    memory_key="chat_history"
)

# Clear memory
memory.clear()
```

## Error Diagnosis Flow

1. **See error type** (ValueError, KeyError, etc.)
2. **Find YOUR code** in stack trace
3. **Check error message** for clues
4. **Use diagnosis tools** or this reference
5. **Apply fix** and test

## Common Patterns

### Creating an Agent
```python
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)
```

### Calling an Agent
```python
# Always use dict format
result = agent.invoke({"input": "your query"})
output = result.get('output', str(result))
```

### Creating a Tool
```python
Tool(
    name="ToolName",
    func=your_function,
    description="Clear description. Input should be X format."
)
```

## Quick Fixes Checklist

- [ ] Using `.invoke()` not `.run()`?
- [ ] Input is `{"input": query}` format?
- [ ] Tool descriptions are clear?
- [ ] All tool functions accept parameters?
- [ ] Config.ini settings correct?
- [ ] LLM server running?
- [ ] Virtual environment activated?

## Need More Help?

1. Check `UNDERSTANDING_ERRORS.md`
2. Run `python system_check.py`
3. Enable verbose mode in config
4. Check the examples in `examples/`

Remember: Most errors are just format issues!
