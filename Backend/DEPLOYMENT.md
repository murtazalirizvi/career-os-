# Deployment Guide: Feature 1 Lens Engine Hardening

## Environment Configuration

### Required Environment Variables

The Feature 1 Lens Engine Hardening enhancements require the following environment variables:

```bash
# Gemini API Key (required for AI-powered recommendations)
GEMINI_API_KEY=your_gemini_api_key_here

# Alternative: Google API Key (if GEMINI_API_KEY is not set)
GOOGLE_API_KEY=your_google_api_key_here
```

### Optional Configuration

The system uses sensible defaults, but you can customize:

- **Gemini API Timeout**: Default 20 seconds (configured in `gemini_client.py`)
- **Cache Size**: Default 10 entries (configured in `feature1_engine.py`)
- **PDF Size Limit**: Default 5MB (configured in `feature1.py`)

## Features Enabled

### 1. Gemini-Powered AI Recommendations
- **Status**: Graceful degradation enabled
- **Behavior**: If GEMINI_API_KEY is not set, the system continues with heuristic recommendations only
- **Endpoint**: POST `/api/feature1/analyze`

### 2. Job Description Quality Analysis
- **Endpoint**: POST `/api/feature1/analyze-jd`
- **Input**: Job description text (1-10,000 characters)
- **Output**: Quality score (0-100), grade, issues, and AI feedback

### 3. Latest Analysis Shortcut
- **Endpoint**: GET `/api/feature1/candidate/{candidate_id}/latest`
- **Behavior**: Returns the most recent analysis without listing all versions

### 4. Resume Text Caching
- **Type**: LRU cache with 10-entry maximum
- **Behavior**: Automatically caches parsed PDF text to avoid re-parsing
- **Performance**: Up to 90% reduction in PDF parsing overhead for repeated requests

### 5. Raw Resume Text Storage
- **Storage**: Automatically stored in database (truncated to 8000 characters)
- **Purpose**: Enables cross-feature resume reuse (e.g., Feature 5 consistency checks)

## Monitoring and Observability

### Key Metrics to Monitor

1. **Gemini API Success/Failure Rates**
   - Monitor for failures >10% over 5 minutes
   - Check logs for timeout or rate limiting issues

2. **Cache Hit/Miss Ratios**
   - Expected hit rate: 60-80% for typical workloads
   - Miss rate >80% indicates potential caching issues

3. **PDF Processing Performance**
   - Expected processing time: <5 seconds for typical resumes
   - Alert if processing time >30 seconds

4. **Analysis Completion Times**
   - With Gemini: 3-10 seconds
   - Without Gemini: 1-3 seconds

### Logging

The system logs AI service failures for monitoring without exposing internal errors to users:

```python
logging.getLogger("career_os").error("Gemini API failure: %s", error_details)
```

## Deployment Steps

### 1. Set Environment Variables

Add the Gemini API key to your environment:

```bash
# Linux/Mac
export GEMINI_API_KEY="your_api_key_here"

# Windows PowerShell
$env:GEMINI_API_KEY="your_api_key_here"

# Windows CMD
set GEMINI_API_KEY=your_api_key_here
```

Or add to your `.env` file:

```
GEMINI_API_KEY=your_api_key_here
```

### 2. Verify Database Schema

The system automatically handles database schema updates. Verify the new fields exist:

```python
# Feature1Analysis model includes:
- ai_recommendations_json: str = Field(default="[]")
- raw_resume_text: str = Field(default="")
```

### 3. Test API Endpoints

Test the new endpoints:

```bash
# Test JD quality analysis
curl -X POST "http://localhost:8000/api/feature1/analyze-jd" \
  -H "Content-Type: application/json" \
  -d '{"jd_text": "We are looking for a senior Python developer with 5+ years experience in FastAPI, PostgreSQL, and AWS."}'

# Test latest analysis retrieval
curl "http://localhost:8000/api/feature1/candidate/test-candidate/latest"
```

### 4. Verify Gemini Integration

Check if Gemini is available:

```python
from app.analysis import gemini_client

if gemini_client.is_available():
    print("Gemini API is configured and available")
else:
    print("Gemini API is not available - system will use heuristic recommendations only")
```

## Backward Compatibility

### API Compatibility
- All existing endpoints maintain identical response formats
- New fields (`ai_recommendations`) are optional and have sensible defaults
- Existing client applications continue to function without modification

### Database Compatibility
- New fields have default values (`[]` for ai_recommendations_json, `""` for raw_resume_text)
- Existing analyses remain accessible
- No data migration required

## Security Considerations

### API Key Management
- Store Gemini API key in environment variables, never in code
- Use least-privilege API key permissions
- Implement key rotation procedures
- Monitor API usage for anomalies

### Input Validation
- PDF uploads limited to 5MB
- Job descriptions limited to 10,000 characters
- File type validation enforces PDF-only uploads

### Data Privacy
- Raw resume text truncated to 8000 characters
- No sensitive information logged in error messages
- Secure deletion of temporary files

## Troubleshooting

### Gemini API Not Working

**Symptom**: AI recommendations are empty

**Solutions**:
1. Verify GEMINI_API_KEY is set: `echo $GEMINI_API_KEY`
2. Check API key validity at https://makersuite.google.com/app/apikey
3. Verify network connectivity to Google's API
4. Check logs for timeout or rate limiting errors

### Cache Not Working

**Symptom**: PDF parsing is slow on repeated requests

**Solutions**:
1. Verify LRU cache is enabled (check `@lru_cache(maxsize=10)` decorator)
2. Check if file paths are consistent (cache key is file path string)
3. Monitor cache hit/miss ratios in logs

### PDF Upload Failures

**Symptom**: 413 error on PDF upload

**Solutions**:
1. Verify PDF size is under 5MB
2. Check if file is actually a PDF (not renamed image or document)
3. Verify PDF is not corrupted

## Performance Optimization

### Caching Strategy
- LRU cache reduces PDF parsing overhead by up to 90%
- Cache warming: Pre-populate with frequently accessed resumes
- Monitor cache effectiveness with hit/miss metrics

### Database Optimization
- Proper indexing on `candidate_id` and `version_number` fields
- Efficient latest analysis retrieval with ORDER BY optimization
- Connection pooling for concurrent request handling

### External Service Optimization
- Optimized Gemini prompts to minimize token usage
- Appropriate temperature settings (0.3) for consistent results
- Circuit breaker pattern for service failures

## Support

For issues or questions:
1. Check logs for error messages
2. Verify environment configuration
3. Test individual components (Gemini client, PDF parsing, database)
4. Review API documentation at `/docs` endpoint
