# Product Similarity Graph

## Overview
Interactive graph visualization showing product similarities based on user engagement patterns using cosine similarity algorithm.

## Files Structure

```
static/similarity/
├── graph.css          # Professional styling (clean, corporate design)
├── graph.js           # D3.js graph logic with force simulation
└── README.md         # This file
```

## Features

### 1. **Similarity Calculation**
- **Algorithm**: Cosine Similarity
- **Engagement Score**: `(clicks × 2) + (view_time × 0.01)`
- **Matrix**: User-Product engagement matrix

### 2. **Graph Visualization**
- **Nodes**: Products (size = total engagement)
- **Edges**: Similarity connections (thickness = similarity strength)
- **Edge Labels**: Similarity scores in percentages
- **Layout**: Force-directed with improved spacing
- **Interactions**: 
  - Drag nodes to rearrange
  - Scroll to zoom in/out
  - Hover for tooltips

### 3. **Professional Design**
- Clean white/gray/blue color scheme
- Subtle shadows and borders
- Responsive layout
- Separation of concerns (CSS/JS/HTML)

## Usage

### Endpoint
```
GET /product-similarity?threshold=0.1
```

**Parameters:**
- `threshold` (optional): Minimum similarity to show connection (0.0-1.0), default=0.1

### Examples
- Show all connections > 10%: `/product-similarity`
- Show only strong connections > 50%: `/product-similarity?threshold=0.5`
- Show even weak connections > 5%: `/product-similarity?threshold=0.05`

## Technical Details

### Force Simulation Parameters
- **Link Distance**: `350 * (1 - similarity * 0.3)` - Similar products stay closer
- **Charge**: `-800` - Strong repulsion keeps nodes apart
- **Collision**: `60` - Prevents overlap

### Color Scheme
- **Nodes**: Blue (#3b82f6)
- **Edges**: Blue to Green gradient (based on similarity)
- **Labels**: Dark gray (#64748b)
- **Background**: Light gray (#f8fafc)

## Dependencies
- **D3.js v7**: For graph visualization (loaded via CDN)
- **NumPy**: Matrix operations
- **Scikit-learn**: Cosine similarity calculation

