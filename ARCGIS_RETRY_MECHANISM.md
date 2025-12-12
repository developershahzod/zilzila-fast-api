# ArcGIS Sync - Automatic Retry Mechanism

## Overview

The ArcGIS sync now includes **automatic retry logic** with exponential backoff to handle transient errors and improve reliability.

## Features

### ✅ Automatic Retries
- **Max retries**: 3 attempts per batch (4 total tries including initial attempt)
- **Exponential backoff**: 2s, 4s, 8s between retries
- **Smart error handling**: Different strategies for different error types

### ✅ Error Types Handled

#### 1. **Server Errors** (Retryable)
- HTTP 500 (Internal Server Error)
- HTTP 502 (Bad Gateway)
- HTTP 503 (Service Unavailable)
- HTTP 504 (Gateway Timeout)

**Action**: Automatic retry with exponential backoff

#### 2. **Network Errors** (Retryable)
- Connection timeout
- Connection refused
- Network unreachable

**Action**: Automatic retry with exponential backoff

#### 3. **Token Errors** (Non-retryable)
- Error code 498 (Invalid token)
- Error code 499 (Token required)

**Action**: Stop immediately, regenerate token on next sync

#### 4. **Partial Success** (Smart handling)
- Some features succeed, some fail in same batch

**Action**: Return success with actual count sent

## How It Works

### Retry Flow

```
Attempt 1: Send batch
  ↓ (fails)
Wait 2 seconds
  ↓
Attempt 2: Retry same batch
  ↓ (fails)
Wait 4 seconds
  ↓
Attempt 3: Retry same batch
  ↓ (fails)
Wait 8 seconds
  ↓
Attempt 4: Final retry
  ↓ (fails)
Mark batch as failed
Continue to next batch
```

### Example Log Output

```
📦 Processing batch 1/143 (100 features)
📤 Sending 100 features to ArcGIS... (attempt 1/4)
❌ Server error 503 - will retry
🔄 Retry attempt 1/3 after 2s...
📤 Sending 100 features to ArcGIS... (attempt 2/4)
✅ Successfully sent 100/100 features to ArcGIS
✅ Batch 1/143 completed: 100 features sent
```

## Configuration

### Retry Settings

Located in `app/arcgis_sync_scheduler.py`:

```python
def send_features_to_arcgis(features: List[Dict], token: str, max_retries: int = 3):
    # max_retries = 3 means 4 total attempts (1 initial + 3 retries)
```

### Batch Size

```python
batch_size = 100  # Send 100 features per batch
```

### Timeout

```python
timeout=60  # 60 seconds per request
```

## Benefits

### 1. **Improved Reliability**
- Handles temporary network issues
- Recovers from server overload
- Reduces failed batches significantly

### 2. **Better Resource Usage**
- Exponential backoff prevents server overload
- Smart error detection avoids unnecessary retries
- Continues processing other batches even if one fails

### 3. **Detailed Logging**
- Shows retry attempts in logs
- Reports exact error types
- Tracks success/failure per batch

### 4. **Partial Success Handling**
- If 80/100 features succeed, counts as success
- Reports actual number sent
- Doesn't retry already-successful features

## Statistics Tracking

After sync completes:

```json
{
  "statistics": {
    "total_sent": 14200,      // Actual features sent successfully
    "total_skipped": 100,     // Duplicates skipped
    "last_error": "5 batches failed"  // Only truly failed batches
  }
}
```

## Error Scenarios

### Scenario 1: Temporary Network Issue
```
Batch 1: Fails (timeout)
  → Retry 1: Fails (timeout)
  → Retry 2: Success ✅
Result: Batch succeeds, 100 features sent
```

### Scenario 2: Server Overload
```
Batch 1: Fails (503 Service Unavailable)
  → Wait 2s
  → Retry 1: Fails (503)
  → Wait 4s
  → Retry 2: Success ✅
Result: Batch succeeds, 100 features sent
```

### Scenario 3: Invalid Token
```
Batch 1: Fails (499 Token required)
  → No retry (token error)
  → Stop sync
  → Will regenerate token on next scheduled sync
Result: Sync stops, token will be refreshed
```

### Scenario 4: Partial Success
```
Batch 1: 80 succeed, 20 fail
  → Return success with count=80
  → No retry (partial success accepted)
Result: 80 features sent, batch marked as success
```

### Scenario 5: All Retries Exhausted
```
Batch 1: Fails
  → Retry 1: Fails
  → Retry 2: Fails
  → Retry 3: Fails
Result: Batch marked as failed, continue to next batch
```

## Monitoring

### Check Retry Activity in Logs

Look for these indicators:

```bash
# Successful retry
🔄 Retry attempt 1/3 after 2s...
✅ Successfully sent 100/100 features to ArcGIS

# Failed after retries
❌ Failed to send batch after 4 attempts. Last error: HTTP 500

# Partial success
⚠️ Sent 80/100 features (20 failed)
```

### API Endpoints

**Check sync status**:
```bash
curl http://localhost:8005/arcgis-sync-status
```

**Trigger manual sync**:
```bash
curl -X POST http://localhost:8005/arcgis-sync-manual
```

## Performance Impact

### Time Estimates

**Without retries**:
- 143 batches × 1 second = ~143 seconds (2.4 minutes)

**With retries** (worst case - all fail once):
- 143 batches × (1s + 2s retry) = ~429 seconds (7.2 minutes)

**With retries** (typical - 95% success rate):
- 136 batches × 1s + 7 batches × 3s = ~157 seconds (2.6 minutes)

### Exponential Backoff Benefits

- Prevents server overload
- Gives server time to recover
- Reduces cascading failures
- More likely to succeed on retry

## Best Practices

### 1. Monitor Logs
Check application logs regularly for retry patterns:
```bash
tail -f app.log | grep "Retry attempt"
```

### 2. Adjust Retry Count
If you see many retries succeeding on 2nd/3rd attempt, current settings are good.
If most fail after all retries, may need to investigate server issues.

### 3. Check Error Patterns
- Many 503 errors → Server capacity issue
- Many timeouts → Network issue
- Many 499 errors → Token generation issue

### 4. Use Manual Sync for Testing
Test retry mechanism:
```bash
curl -X POST http://localhost:8005/arcgis-sync-manual
```

## Code Changes Summary

### Modified Files

1. **`app/arcgis_sync_scheduler.py`**
   - Added `time` import for sleep
   - Added `Tuple` type hint
   - Updated `send_features_to_arcgis()` signature to return `Tuple[bool, int]`
   - Added retry loop with exponential backoff
   - Added smart error detection
   - Added partial success handling
   - Updated sync task to use new return values

### Function Signature Change

**Before**:
```python
def send_features_to_arcgis(features: List[Dict], token: str) -> bool:
```

**After**:
```python
def send_features_to_arcgis(features: List[Dict], token: str, max_retries: int = 3) -> Tuple[bool, int]:
```

## Testing

### Test Retry Mechanism

1. **Restart application** with new code
2. **Trigger manual sync**:
   ```bash
   ./trigger_manual_sync.sh
   ```
3. **Watch logs** for retry activity
4. **Check results**:
   ```bash
   curl http://localhost:8005/arcgis-sync-status
   ```

### Expected Improvements

**Before** (no retries):
```json
{
  "total_sent": 0,
  "total_skipped": 0,
  "last_error": "143 batches failed"
}
```

**After** (with retries):
```json
{
  "total_sent": 14200,
  "total_skipped": 100,
  "last_error": null  // or "2 batches failed" (much better!)
}
```

## Summary

✅ **Automatic retry** with 3 attempts per batch  
✅ **Exponential backoff** (2s, 4s, 8s)  
✅ **Smart error handling** for different error types  
✅ **Partial success** support  
✅ **Detailed logging** for monitoring  
✅ **No configuration needed** - works automatically  

The retry mechanism significantly improves sync reliability and reduces the number of failed batches from transient errors.
