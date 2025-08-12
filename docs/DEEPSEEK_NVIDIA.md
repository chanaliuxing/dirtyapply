# DeepSeek R1 via NVIDIA API Integration

Apply-Copilot supports DeepSeek R1 model through NVIDIA's AI platform, providing access to cutting-edge reasoning capabilities.

## Configuration

### 1. Get NVIDIA API Key

1. Visit [NVIDIA NIM](https://build.nvidia.com/deepseek-ai/deepseek-r1)
2. Sign up or log in to your NVIDIA account
3. Generate an API key (starts with `nvapi-`)

### 2. Environment Configuration

Add to your `.env` file:

```bash
# Set LLM provider to use DeepSeek via NVIDIA
LLM_PROVIDER=deepseek-nvidia

# Your NVIDIA API key (starts with nvapi-)
DEEPSEEK_NVIDIA_API_KEY=nvapi-your-actual-api-key-here
```

## Usage

### API Integration

The DeepSeek NVIDIA provider is automatically used when configured. It supports:

- **Model**: `deepseek-ai/deepseek-r1` (default)
- **Temperature**: `0.6` (optimized for reasoning)
- **Top-P**: `0.7` (balanced creativity)
- **Max Tokens**: `4096` (configurable)
- **Streaming**: Full streaming support

### Example API Call

Test the integration with the debug endpoint:

```bash
curl -X POST "http://localhost:8000/api/llm/test" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain your reasoning capabilities"}
    ],
    "max_tokens": 500
  }'
```

Expected response:
```json
{
  "provider": "deepseek-nvidia",
  "response": "DeepSeek R1 response with reasoning...",
  "status": "success",
  "model_info": "Uses DeepSeek R1 via NVIDIA API"
}
```

### JTR Integration

When using DeepSeek NVIDIA for Job-Tailored Resume generation:

```bash
curl -X POST "http://localhost:8000/api/jtr" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Senior Data Scientist",
    "job_description": "Looking for ML expert...",
    "resume_profile": {...}
  }'
```

## Technical Implementation

### Client Configuration

The service uses the OpenAI client with NVIDIA's base URL:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="nvapi-your-key"
)
```

### Streaming Support

Full streaming implementation for real-time responses:

```python
async for chunk in client.chat.completions.create(
    model="deepseek-ai/deepseek-r1",
    messages=messages,
    temperature=0.6,
    top_p=0.7,
    max_tokens=4096,
    stream=True
):
    if chunk.choices[0].delta.content is not None:
        yield chunk.choices[0].delta.content
```

## Security & Best Practices

### ✅ Security Compliance

- **No Hard-coded Keys**: API keys from environment variables only
- **Safe Logging**: Keys automatically masked in logs (`nvapi-12345678***`)
- **Validation**: Startup fails if key format is invalid
- **Fail-safe**: Falls back to rule-based provider on error

### ✅ Golden Rules Implementation

```python
@validator("deepseek_nvidia_api_key")
def validate_deepseek_nvidia_key(cls, v):
    if v and not v.startswith('nvapi-'):
        raise ValueError("Invalid DeepSeek NVIDIA API key format - must start with 'nvapi-'")
    return v
```

### ✅ Logging Example

```bash
2024-01-15 INFO Configuration loaded deepseek_nvidia_api_key=nvapi-ZwdrWQiv***
2024-01-15 INFO DeepSeek NVIDIA provider initialized
```

## Reasoning Capabilities

DeepSeek R1 excels at:

### 📊 Resume Analysis
- **Skills Gap Analysis**: Identifies missing qualifications
- **Experience Mapping**: Maps candidate experience to job requirements  
- **ATS Optimization**: Suggests keyword improvements
- **Evidence-based Enhancement**: Recommends reasonable improvements with justification

### 🎯 Job Matching
- **Requirement Parsing**: Extracts must-have vs. preferred qualifications
- **Scoring Logic**: Provides detailed match score breakdown
- **Risk Assessment**: Evaluates enhancement safety levels
- **Reasoning Chains**: Shows step-by-step analysis

## Error Handling

### Provider Fallback

If NVIDIA API fails, the system automatically falls back:

```python
except Exception as e:
    logger.error(f"DeepSeek NVIDIA API error: {e}")
    logger.info("Falling back to rule-based provider")
    return RuleBasedProvider()
```

### Rate Limiting

NVIDIA API includes built-in rate limiting. The service handles:

- Automatic retry with exponential backoff
- Graceful degradation to rule-based mode
- Clear error messages for quota exceeded

## Comparison with Other Providers

| Feature | DeepSeek-NVIDIA | OpenAI | Anthropic | Rule-Based |
|---------|-----------------|---------|-----------|------------|
| Reasoning | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Speed | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Cost | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Offline | ❌ | ❌ | ❌ | ✅ |
| Streaming | ✅ | ✅ | ✅ | ✅ |

## Troubleshooting

### Common Issues

**Error: Invalid API key format**
```bash
# Ensure key starts with nvapi-
DEEPSEEK_NVIDIA_API_KEY=nvapi-your-key-here
```

**Error: Provider initialization failed**
```bash
# Check logs for specific error
docker logs apply-copilot-api

# Test provider directly
curl http://localhost:8000/api/llm/test
```

**Error: Rate limit exceeded**
```bash
# System automatically falls back to rule-based mode
# Check logs for fallback confirmation
```

### Debug Commands

```bash
# Validate configuration
make validate-env

# Test LLM integration
curl -X POST http://localhost:8000/api/llm/test -d '{"messages": [{"role": "user", "content": "test"}]}'

# Check service health
curl http://localhost:8000/health
```

## Next Steps

With DeepSeek NVIDIA configured, you can:

1. **Test Integration**: Use `/api/llm/test` endpoint
2. **Try JTR**: Submit job descriptions for analysis
3. **Enable Streaming**: For real-time responses
4. **Monitor Performance**: Track reasoning quality vs. other providers
5. **Scale Usage**: Leverage NVIDIA's infrastructure for high-volume processing

The DeepSeek R1 integration provides state-of-the-art reasoning capabilities while maintaining Apply-Copilot's security and reliability standards.