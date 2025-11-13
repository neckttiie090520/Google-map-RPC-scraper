# Troubleshooting Guide

This document provides solutions to common issues encountered when using the Google Maps RPC Scraper.

## 🔧 Common Issues and Solutions

### 1. Scraper Returns 0 Reviews

**Problem**: Scraper runs successfully but returns 0 reviews.

**Symptoms**:
- Task shows "completed" but 0 reviews scraped
- No error messages in console
- UI shows "ไม่พบรีวิว" (No reviews found)

**Root Causes & Solutions**:

#### A. Import/Module Issues ✅ FIXED (2025-11-13)
- **Error**: `NameError: name 'PBAnalysisResult' is not defined`
- **Fix**: Updated import fallback in `production_scraper.py:45-53`
- **Status**: Resolved

#### B. httpx Compatibility Issues ✅ FIXED (2025-11-13)
- **Error**: `AttributeError: module 'httpx' has no attribute 'Limits'`
- **Fix**: Removed unsupported `limits` and `follow_redirects` parameters
- **Status**: Resolved

#### C. Place ID Issues
- **Check**: Verify place ID format `0x30e29ecfc2f455e1:0xc4ad0280d8906604`
- **Test**: Use known working place ID (Central World Bangkok)
- **Solution**: Get fresh place ID via search API

#### D. Rate Limiting
- **Check**: Console for rate limit warnings
- **Solution**: Reduce `max_rate` to 5.0 or enable `fast_mode=False`

### 2. Thai Character Encoding Issues

**Problem**: Thai characters display as `�����` in Windows console.

**Solutions**:
```bash
# Method 1: Set console encoding
chcp 65001

# Method 2: Set environment variable
set PYTHONIOENCODING=utf-8
python webapp/app.py

# Method 3: Run with UTF-8 flag
python -X utf8 webapp/app.py
```

### 3. Flask App Port Conflicts

**Problem**: Cannot start webapp, port already in use.

**Solutions**:
```bash
# Check what's using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F

# Or use different port
python webapp/app.py --port 5001
```

### 4. Translation System Errors 🔴 CURRENT ISSUE

**Problem**: `'float' object has no attribute 'as_dict'` error

**Status**: Temporary issue - translation system disabled

**Workaround**:
1. Disable translation in settings: `enable_translation=False`
2. Set `ENABLE_TRANSLATION=false` in `.env` file
3. Use language-region settings instead of translation

**Long-term Fix**: In progress - requires debug of translation queue processing

### 5. Thai Provinces Search Issues

**Problem**: "จังหวัด ... ไม่พบในระบบ" (Province not found)

**Solutions**:
1. **Check spelling**: Use exact Thai province names
2. **Use aliases**: `chiang mai` for `เชียงใหม่`
3. **API test**: Use `/api/provinces/suggestions?q=เชียง` endpoint
4. **Validate**: Check province exists in `THAI_PROVINCES` dict

### 6. Language-Region Settings Not Applied

**Problem**: Language settings don't affect results.

**Solutions**:
1. **Use correct format**: `"en-th"`, `"ja-jp"`, `"zh-cn"`
2. **Check presets**: Verify in `LANGUAGE_REGION_PRESETS`
3. **Test parsing**: Use `split_language_region()` function
4. **Verify headers**: Check `Accept-Language` in request

### 7. Webapp 404 Errors

**Problem**: Pages return 404, cannot access UI.

**Solutions**:
1. **Check port**: Try `http://localhost:5001` instead of 5000
2. **Single instance**: Ensure only one Flask app running
3. **URL paths**: Verify correct routes in `app.py`
4. **Indentation**: Check Python indentation in route definitions

### 8. Performance Issues

**Problem**: Scraping is very slow (< 5 reviews/sec).

**Solutions**:
1. **Fast mode**: Ensure `fast_mode=True`
2. **Rate settings**: Check `max_rate` (default 10.0)
3. **Network latency**: Especially with proxies
4. **Rate limiting**: Monitor auto-slowdown in logs

### 9. Memory Issues

**Problem**: High memory usage during large scrapes.

**Solutions**:
1. **Review limit**: Set reasonable `max_reviews`
2. **Stream output**: Enable streaming for very large datasets
3. **Task cleanup**: Delete completed tasks regularly
4. **Restart service**: Periodic service restart for long-running

## 🧪 Testing & Debugging

### Quick Test Script
```bash
# Run standalone test
python test_simple.py

# Expected output:
# - 20 reviews from Central World
# - 26-30 reviews/sec rate
# - No import errors
```

### Debug Mode
Enable debug logging in production_scraper.py:
```python
# Uncomment debug prints in parse_review()
# print(f"DEBUG: Full el structure: {json.dumps(el, indent=2, ensure_ascii=False)}")
```

### Console Logs
Monitor Flask console for:
- Import errors
- HTTP request failures
- Rate limit warnings
- Translation errors

## 📊 Performance Benchmarks

### Expected Performance:
- **Fast Mode**: 26-40+ reviews/sec
- **Human Mode**: ~10 reviews/sec
- **Conservative**: 3-5 reviews/sec

### Factors Affecting Performance:
- Fast vs Human mode: 3-4x difference
- Proxy usage: ~10-20% slower
- Rate limiting: Auto-slowdown
- Date filtering: Early termination

## 🆘 Getting Help

### Log Analysis
1. **Scraper logs**: Check `production_scraper.py` console output
2. **Flask logs**: Monitor Flask app console
3. **Browser console**: F12 → Network tab for API failures
4. **Error traces**: Full stack traces for debugging

### Common Debug Steps
1. **Test standalone**: `python test_simple.py`
2. **Check imports**: Verify no import errors
3. **Verify API**: Test with known working place ID
4. **Monitor console**: Watch for error messages
5. **Check settings**: Verify `.env` and webapp settings

### Reporting Issues
When reporting issues, include:
1. **Full error message** and stack trace
2. **Console output** from both scraper and Flask app
3. **Settings used** (language, region, place ID)
4. **Steps to reproduce** the issue
5. **Expected vs actual behavior**

---

**Last Updated**: 2025-11-13
**Version**: v2.0 (Post-cleanup)
**Status**: Production Ready (Translation disabled temporarily)