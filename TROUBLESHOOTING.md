# 🔧 LangEntiChain Troubleshooting Guide

## Common Issues and Solutions

### 1. Agent Gets Stuck or Loops
**Symptoms**: Agent repeats the same action multiple times

**Solutions**:
- Check that your LLM model supports tool calling properly
- Try a different model (some models handle agents better)
- Increase `temperature` in config.ini to 0.8 or 0.9
- Ensure tools are returning clear, parseable responses

### 2. White Background in Dark Mode
**Symptoms**: Chat messages have white background even in dark theme

**Solutions**:
- Hard refresh the browser (Ctrl+F5)
- Clear browser cache
- The CSS fixes should handle this automatically

### 3. File Write Errors
**Symptoms**: Agent can't create files

**Solutions**:
- Check file permissions in the directory
- Use absolute paths if relative paths fail
- Ensure no special characters in filenames
- Remember the format: `filename|content`

### 4. Import Errors
**Symptoms**: ModuleNotFoundError for langchain packages

**Solutions**:
```bash
# Clean reinstall
pip uninstall langchain langchain-community langchain-core -y
pip install -r requirements.txt
```

### 5. LM Studio Connection Failed
**Symptoms**: Can't connect to LM Studio

**Solutions**:
- Ensure LM Studio server is running
- Check it's on port 1234 (default)
- Model must be loaded in LM Studio
- Try http://localhost:1234/v1/models to verify

### 6. Ollama Connection Failed
**Symptoms**: Can't connect to Ollama

**Solutions**:
- Run `ollama serve` in terminal
- Pull your model: `ollama pull model-name`
- Check port 11434 is available
- Verify with: `curl http://localhost:11434/api/tags`

### 7. Agent Timeout
**Symptoms**: Agent stops after long execution

**Solutions**:
- Increase `max_execution_time` in config.ini
- Break complex tasks into smaller steps
- Check if model is actually responding (not frozen)

### 8. Crypto Prices Not Real
**Symptoms**: Bitcoin/Ethereum prices are simulated

**Solutions**:
- Current implementation uses simulated data
- To get real prices, integrate CoinGecko API:
  - Get free API key from CoinGecko
  - Replace `_get_crypto_prices()` function
  - Add `requests` call to their API

### 9. Memory/Context Issues
**Symptoms**: Agent forgets previous conversation

**Solutions**:
- ConversationBufferMemory is working but has limits
- For long conversations, consider ConversationSummaryMemory
- Clear chat history if context gets too large

### 10. Slow Response Times
**Symptoms**: Agent takes long to respond

**Solutions**:
- Check model size vs. your hardware
- Use smaller/faster models for testing
- Reduce `max_tokens` in config.ini
- Disable `verbose` mode for production use

## Debug Mode

Add this to your config.ini for maximum debugging:
```ini
[AGENT]
verbose = true
return_intermediate_steps = true
```

Then check the console output when running the app.

## Getting Help

If issues persist:
1. Run `python test_agent.py` to diagnose
2. Check console/terminal for detailed errors
3. Verify all services are running
4. Try with a simpler prompt first
