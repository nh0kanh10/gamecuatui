# Performance Analysis - Cultivation Simulator

## Current Performance Metrics

### Character Creation (POST /game/new)
- **Total Time**: ~19.8 seconds
- **Breakdown**:
  - Game initialization: ~0.1s
  - AI API call: ~19.7s (99% of total time)
  - State saving: ~0.03s

### Year Turn (POST /game/action)
- **Total Time**: ~19.4 seconds
- **Breakdown**:
  - ECS tick: ~0.03s
  - AI API call: ~19.3s (99% of total time)
  - State updates: ~0.04s

## Bottlenecks

1. **AI API Response Time** (~19s)
   - Primary bottleneck: Gemini API latency
   - Model: gemini-2.5-pro (slower but higher quality)
   - Prompt length: ~6882 chars (~1700 tokens)
   - Response length: ~1607 chars (~400 tokens)

2. **Network Latency**
   - API calls to Google's servers
   - No caching of responses

3. **Prompt Size**
   - Memory context can be large
   - World database context included

## Optimization Strategies

### ✅ Implemented

1. **Model Selection**
   - Default: `gemini-2.5-flash` (faster than pro)
   - Fallback chain prioritizes fast models

2. **Prompt Optimization**
   - Truncate memory context if > 8000 chars
   - Limit prompt to ~20000 chars (~5000 tokens)

3. **Generation Config**
   - `max_output_tokens`: 2048 (reduced from 4096)
   - Faster response while maintaining quality

4. **Rate Limiting**
   - Reduced delay: 0.5s (from 1.0s)
   - Faster consecutive requests

### 🔄 Recommended Next Steps

1. **Streaming Responses** (if API supports)
   - Show partial narrative while AI generates
   - Perceived performance improvement

2. **Response Caching**
   - Cache common responses (e.g., fallback narratives)
   - Reduce API calls for repeated scenarios

3. **Parallel Processing**
   - Pre-generate next turn choices while user reads
   - Background generation

4. **Model Comparison**
   - Test `gemini-2.5-flash` vs `gemini-2.0-flash-001`
   - Measure actual response times

5. **Prompt Engineering**
   - Further reduce prompt size
   - Use more concise instructions
   - Remove redundant context

## Target Performance

- **Character Creation**: < 10s (50% improvement)
- **Year Turn**: < 10s (50% improvement)
- **Perceived Latency**: < 5s (with streaming)

## Current Status

- ✅ Model optimized (flash instead of pro)
- ✅ Prompt truncation implemented
- ✅ Generation config optimized
- ✅ Rate limiting optimized
- ⏳ Streaming (not yet implemented)
- ⏳ Caching (not yet implemented)

