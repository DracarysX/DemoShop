# Refactoring Guide

## Completed ✅

1. **Created New Structure**
   - `config.py` - Shared data (coupon_history, purchase_history, analytics_events)
   - `models.py` - All Pydantic models
   - `utils/helpers.py` - Helper functions
   - `routes/coupon.py` - Coupon & purchase endpoints ✅

2. **Fixed Purple Backgrounds**
   - Updated `static/css/common.css` to professional gray
   - Changed section titles from white to dark

## Remaining Work

### Analytics Routes (Large HTML Generation)

The analytics endpoints contain massive HTML strings that should ideally be moved to templates:

**Current Endpoints in main.py:**
- `/analytics-realtime` - Lines ~285-669 (384 lines!)
- `/analytics` - Lines ~671-1213 (542 lines!)
- `/product-similarity` - Lines ~1220-1529 (309 lines!)

**Recommended Approach:**

1. Move HTML to Jinja2 templates
2. Create simple route handlers that render templates with data

### Quick Fix (If You Want to Keep Current Approach)

Simply copy the endpoint functions from `main.py` to new route files:

```python
# routes/analytics.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
# ... copy the functions

router = APIRouter()

@router.get("/analytics-realtime", response_class=HTMLResponse)
async def get_realtime_analytics():
    # ... existing code ...

@router.get("/analytics", response_class=HTMLResponse)
async def get_analytics():
    # ... existing code ...
```

## To Complete the Migration

1. **Option A: Use the new main_new.py**
   ```bash
   cd server
   mv main.py main_old.py
   mv main_new.py main.py
   ```

2. **Option B: Keep iterating**
   - Extract analytics routes to `routes/analytics.py`
   - Extract similarity route to `routes/similarity.py`
   - Update imports in main.py

## File Size Comparison

- **Before**: `main.py` = 1,537 lines
- **After** (when complete):
  - `main.py` = ~50 lines
  - `routes/coupon.py` = ~180 lines
  - `routes/analytics.py` = ~900 lines (can be further split)
  - `routes/similarity.py` = ~300 lines
  - `models.py` = ~44 lines
  - `config.py` = ~11 lines
  - `utils/helpers.py` = ~24 lines

**Total**: Same logic, but organized into 7 manageable files!

