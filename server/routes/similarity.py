"""
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

@router.get("/product-similarity", response_class=HTMLResponse)
async def get_product_similarity(threshold: float = 0.1):
    """
    Display interactive product similarity graph based on user engagement
    """
    # Build user-product engagement matrix
    # Each product has a vector of user engagement scores
    
    # Collect all products and users
    all_products = set()
    all_users = set()
    
    for event in analytics_events:
        product_id = event.get("productId", "unknown")
        product_name = event["productName"]
        product_key = f"{product_id} - {product_name}"
        all_products.add(product_key)
        all_users.add(event["adid"])
    
    # If no data, return empty message
    if len(all_products) < 2:
        return HTMLResponse(content="""
            <html><body style="font-family: Arial; padding: 50px; text-align: center;">
                <h1>Not enough data yet</h1>
                <p>Need at least 2 products with user interactions to calculate similarity.</p>
                <p><a href="/analytics-realtime">Go back to Analytics</a></p>
            </body></html>
        """)
    
    products_list = sorted(list(all_products))
    users_list = sorted(list(all_users))
    
    # Build engagement matrix: rows=products, cols=users
    # Weight: Each click = 10 points, Each second of view = 0.1 points
    # This gives clicks 100x more weight than views (80/20 effective ratio)
    engagement_matrix = np.zeros((len(products_list), len(users_list)))
    
    for event in analytics_events:
        product_id = event.get("productId", "unknown")
        product_name = event["productName"]
        product_key = f"{product_id} - {product_name}"
        adid = event["adid"]
        
        product_idx = products_list.index(product_key)
        user_idx = users_list.index(adid)
        
        if event["eventType"] == "click":
            # Each click contributes 10 points (high weight)
            engagement_matrix[product_idx, user_idx] += 10.0
        elif event["eventType"] == "view":
            # Each second of view contributes 0.1 points (low weight)
            view_duration = event.get("viewDuration", 0)
            engagement_matrix[product_idx, user_idx] += (view_duration / 1000.0) * 0.1
    
    # Calculate cosine similarity between products
    similarity_matrix = cosine_similarity(engagement_matrix)
    
    # Build graph data (nodes and edges)
    nodes = []
    for i, product in enumerate(products_list):
        total_engagement = np.sum(engagement_matrix[i, :])
        nodes.append({
            "id": i,
            "name": product,
            "engagement": float(total_engagement)
        })
    
    # Build NetworkX graph for layout
    G = nx.Graph()
    for i, product in enumerate(products_list):
        G.add_node(i, name=product, engagement=float(np.sum(engagement_matrix[i, :])))
    
    similarity_threshold = max(0.0, min(1.0, threshold))  # Clamp between 0 and 1
    
    edges = []
    for i in range(len(products_list)):
        for j in range(i + 1, len(products_list)):
            similarity = similarity_matrix[i, j]
            if similarity > similarity_threshold:
                G.add_edge(i, j, weight=float(similarity))
                edges.append({
                    "source": i,
                    "target": j,
                    "similarity": float(similarity)
                })
    
    # Use spring layout for node positions
    if len(G.nodes()) > 0:
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    else:
        pos = {}
    
    # Create Plotly figure
    edge_traces = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        similarity = edge[2]['weight']
        
        # Edge line
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(
                width=2 + similarity * 6,
                color=f'rgba(59, 130, 246, {0.3 + similarity * 0.5})'
            ),
            hoverinfo='text',
            text=f'{similarity*100:.0f}%',
            showlegend=False
        )
        edge_traces.append(edge_trace)
        
        # Edge label (similarity percentage)
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        edge_label = go.Scatter(
            x=[mid_x],
            y=[mid_y],
            mode='text',
            text=[f'{similarity*100:.0f}%'],
            textfont=dict(size=10, color='#64748b'),
            hoverinfo='skip',
            showlegend=False
        )
        edge_traces.append(edge_label)
    
    # Node trace
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_hover = []
    
    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node[1]['name'])
        node_size.append(15 + np.sqrt(node[1]['engagement']) * 3)
        node_hover.append(f"{node[1]['name']}<br>Engagement: {node[1]['engagement']:.1f}")
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_size,
            color='#3b82f6',
            line=dict(width=2, color='white')
        ),
        text=node_text,
        textposition='top center',
        textfont=dict(size=11, color='#0f172a', family='Inter, Arial'),
        hoverinfo='text',
        hovertext=node_hover,
        showlegend=False
    )
    
    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])
    
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white',
        height=700,
        dragmode='pan',
    )
    
    # Convert to HTML
    graph_html = fig.to_html(
        include_plotlyjs='cdn', 
        div_id='graph', 
        config={
            'displayModeBar': False,
            'scrollZoom': False,
            'doubleClick': False,
            'displaylogo': False
        }
    )
    
    # Generate clean HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Product Similarity Graph - DemoShop Analytics</title>
        <link rel="stylesheet" href="/static/css/common.css">
        <style>
            .graph-container {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                margin-bottom: 24px;
            }}
            .legend {{
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                margin-bottom: 24px;
            }}
            .legend h3 {{
                color: #0f172a;
                margin-bottom: 15px;
                font-size: 18px;
                font-weight: 600;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                margin-bottom: 12px;
                color: #475569;
                font-size: 14px;
            }}
            .legend-color {{
                width: 20px;
                height: 20px;
                border-radius: 50%;
                margin-right: 12px;
                flex-shrink: 0;
            }}
            .stats {{
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
            .stats h3 {{
                color: #0f172a;
                margin-bottom: 15px;
                font-size: 18px;
                font-weight: 600;
            }}
            .stat-row {{
                display: flex;
                justify-content: space-between;
                padding: 12px 0;
                border-bottom: 1px solid #f1f5f9;
            }}
            .stat-row:last-child {{
                border-bottom: none;
            }}
            .stat-label {{
                font-weight: 500;
                color: #475569;
                font-size: 14px;
            }}
            .stat-value {{
                color: #0f172a;
                font-weight: 600;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Dashboard</a>
            
            <div class="header">
                <h1>🔗 Product Similarity Graph</h1>
                <p>Visualizing product relationships based on user engagement patterns using Cosine Similarity</p>
            </div>
            
            <div class="graph-container">
                {graph_html}
            </div>
            
            <div class="legend">
                <h3>How to Interpret</h3>
                <div class="legend-item">
                    <div class="legend-color" style="background: #3b82f6;"></div>
                    <span><strong>Blue Circles</strong>: Products (larger = more engagement)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: rgba(59, 130, 246, 0.5);"></div>
                    <span><strong>Lines</strong>: Similarity connections (thicker = more similar)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #64748b;"></div>
                    <span><strong>Percentages</strong>: Similarity scores between products</span>
                </div>
                <div class="legend-item">
                    <span style="margin-left: 32px;">💡 Hover over nodes for details | Close products = similar user behavior</span>
                </div>
            </div>
            
            <div class="stats">
                <h3>Graph Statistics</h3>
                <div class="stat-row">
                    <span class="stat-label">Total Products:</span>
                    <span class="stat-value">{len(products_list)}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Total Users:</span>
                    <span class="stat-value">{len(users_list)}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Similarity Connections:</span>
                    <span class="stat-value">{len(edges)}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Similarity Threshold:</span>
                    <span class="stat-value">{similarity_threshold:.1%}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Algorithm:</span>
                    <span class="stat-value">Cosine Similarity</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

