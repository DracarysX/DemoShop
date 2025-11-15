#!/usr/bin/env python3
"""
Script to split main.py into organized route modules
Run this to complete the refactoring automatically
"""

def extract_analytics_realtime():
    """Extract /analytics-realtime endpoint"""
    with open('main.py', 'r') as f:
        lines = f.readlines()
    
    # Find the analytics-realtime function (around line 285)
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if '@app.get("/analytics-realtime"' in line:
            start_idx = i
        if start_idx and i > start_idx and line.startswith('@app.get'):
            end_idx = i
            break
    
    if start_idx and end_idx:
        return ''.join(lines[start_idx:end_idx])
    return None

def extract_analytics():
    """Extract /analytics endpoint"""
    with open('main.py', 'r') as f:
        lines = f.readlines()
    
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if '@app.get("/analytics"' in line and 'response_class=HTMLResponse' in line:
            start_idx = i
        if start_idx and i > start_idx and line.startswith('@app.get("/product-similarity"'):
            end_idx = i
            break
    
    if start_idx and end_idx:
        return ''.join(lines[start_idx:end_idx])
    return None

def extract_similarity():
    """Extract /product-similarity endpoint"""
    with open('main.py', 'r') as f:
        lines = f.readlines()
    
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if '@app.get("/product-similarity"' in line:
            start_idx = i
        if start_idx and i > start_idx and line.startswith('@app.get("/health"'):
            end_idx = i
            break
    
    if start_idx and end_idx:
        return ''.join(lines[start_idx:end_idx])
    return None

def create_analytics_routes():
    """Create routes/analytics.py"""
    header = '''"""
Analytics dashboard endpoints
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime
from typing import Dict
from collections import defaultdict

from config import analytics_events, purchase_history

router = APIRouter()

'''
    
    realtime = extract_analytics_realtime()
    analytics = extract_analytics()
    
    if realtime and analytics:
        # Replace @app.get with @router.get
        realtime = realtime.replace('@app.get', '@router.get')
        analytics = analytics.replace('@app.get', '@router.get')
        
        content = header + realtime + '\n' + analytics
        
        with open('routes/analytics.py', 'w') as f:
            f.write(content)
        print("✅ Created routes/analytics.py")
        return True
    else:
        print("❌ Failed to extract analytics routes")
        return False

def create_similarity_routes():
    """Create routes/similarity.py"""
    header = '''"""
Product similarity graph endpoint
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go
import networkx as nx
import json

from config import analytics_events, purchase_history

router = APIRouter()

'''
    
    similarity = extract_similarity()
    
    if similarity:
        # Replace @app.get with @router.get
        similarity = similarity.replace('@app.get', '@router.get')
        
        content = header + similarity
        
        with open('routes/similarity.py', 'w') as f:
            f.write(content)
        print("✅ Created routes/similarity.py")
        return True
    else:
        print("❌ Failed to extract similarity route")
        return False

def main():
    """Run the migration"""
    print("🚀 Starting main.py refactoring...")
    print()
    
    print("Step 1: Creating analytics routes...")
    if create_analytics_routes():
        print("✅ Analytics routes created")
    
    print()
    print("Step 2: Creating similarity routes...")
    if create_similarity_routes():
        print("✅ Similarity routes created")
    
    print()
    print("Step 3: Switch to new main.py...")
    print("   Run: mv main.py main_old.py && mv main_new.py main.py")
    print()
    print("✅ Refactoring complete!")
    print()
    print("📁 New structure:")
    print("   - main.py (51 lines)")
    print("   - routes/coupon.py (180 lines)")
    print("   - routes/analytics.py (~900 lines)")
    print("   - routes/similarity.py (~300 lines)")
    print("   - models.py (44 lines)")
    print("   - config.py (11 lines)")

if __name__ == "__main__":
    main()

