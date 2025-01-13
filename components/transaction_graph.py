import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils.data_processing import format_timestamp, format_lamports
import time

def generate_node_positions(transactions, num_nodes):
    """Generate 3D coordinates for nodes in a spherical layout with better spacing"""
    phi = np.linspace(0, 2*np.pi, num_nodes)
    theta = np.linspace(-np.pi/2, np.pi/2, num_nodes)
    r = 10

    x = r * np.outer(np.cos(theta), np.cos(phi)).flatten()
    y = r * np.outer(np.cos(theta), np.sin(phi)).flatten()
    z = r * np.outer(np.sin(theta), np.ones_like(phi)).flatten()

    # Add some random jitter to prevent overlapping
    jitter = np.random.normal(0, 0.5, (3, num_nodes))
    x = x[:num_nodes] + jitter[0]
    y = y[:num_nodes] + jitter[1]
    z = z[:num_nodes] + jitter[2]

    return x, y, z

def create_animated_edge(start_pos, end_pos, frames=30):
    """Create smoother animation frames for transaction flow with arc effect"""
    # Create an arc between points
    t = np.linspace(0, 1, frames)

    # Add an arc height based on distance
    dist = np.linalg.norm(np.array(end_pos) - np.array(start_pos))
    arc_height = dist * 0.3

    # Create arc path
    x_frames = start_pos[0] + (end_pos[0] - start_pos[0]) * t
    y_frames = start_pos[1] + (end_pos[1] - start_pos[1]) * t
    z_frames = start_pos[2] + (end_pos[2] - start_pos[2]) * t + arc_height * np.sin(np.pi * t)

    return x_frames, y_frames, z_frames

def create_transaction_graph(_client, num_transactions=50):
    """Create an interactive 3D visualization of recent transactions with enhanced animation"""
    st.header("🌐 Transaction Network Visualization")

    # Add control panel
    st.sidebar.subheader("Visualization Controls")
    animation_speed = st.sidebar.slider("Animation Speed", 30, 100, 50)
    node_size = st.sidebar.slider("Node Size", 5, 15, 8)
    edge_width = st.sidebar.slider("Edge Width", 1, 5, 3)

    try:
        # Fetch recent transactions
        transactions = _client.get_recent_transactions(num_transactions)

        if not transactions:
            st.warning("No recent transactions available for visualization")
            return

        # Extract unique addresses (nodes)
        addresses = set()
        for tx in transactions:
            addresses.add(tx['from'])
            addresses.add(tx['to'])

        # Create mapping of addresses to indices
        address_to_idx = {addr: idx for idx, addr in enumerate(addresses)}

        # Generate node positions
        x, y, z = generate_node_positions(transactions, len(addresses))

        # Create the base figure with nodes
        fig = go.Figure()

        # Add nodes (addresses) with enhanced visual effects
        node_colors = ['#9945FF' if i % 2 == 0 else '#00FF94' for i in range(len(addresses))]

        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(
                size=node_size,
                color=node_colors,
                opacity=0.8,
                line=dict(
                    color='#FFFFFF',
                    width=1
                ),
                symbol='circle'
            ),
            text=[f"Address: {addr[:8]}...<br>Balance: {format_lamports(_client.get_balance(addr) if addr else 0)} SOL" 
                  for addr in addresses],
            hoverinfo='text',
            name='Addresses'
        ))

        # Create frames for transaction animations
        frames = []
        for frame_idx, tx in enumerate(transactions):
            start_idx = address_to_idx[tx['from']]
            end_idx = address_to_idx[tx['to']]

            # Create animated edge with arc effect
            x_frames, y_frames, z_frames = create_animated_edge(
                (x[start_idx], y[start_idx], z[start_idx]),
                (x[end_idx], y[end_idx], z[end_idx])
            )

            # Create pulse effect
            pulse_sizes = np.linspace(node_size, node_size * 1.5, len(x_frames))

            for step in range(len(x_frames)):
                frame_data = [
                    # Keep the nodes with pulse effect
                    go.Scatter3d(
                        x=x, y=y, z=z,
                        mode='markers',
                        marker=dict(
                            size=[pulse_sizes[step] if i in [start_idx, end_idx] else node_size 
                                 for i in range(len(addresses))],
                            color=node_colors,
                            opacity=0.8,
                            line=dict(
                                color='#FFFFFF',
                                width=1
                            )
                        ),
                        text=[f"Address: {addr[:8]}..." for addr in addresses],
                        hoverinfo='text'
                    ),
                    # Animated transaction line with glow effect
                    go.Scatter3d(
                        x=[x[start_idx], x_frames[step]],
                        y=[y[start_idx], y_frames[step]],
                        z=[z[start_idx], z_frames[step]],
                        mode='lines',
                        line=dict(
                            color='#00FF94',
                            width=edge_width
                        ),
                        opacity=0.8
                    )
                ]

                frames.append(go.Frame(
                    data=frame_data,
                    name=f'frame{frame_idx}_{step}'
                ))

        # Add frames to figure
        fig.frames = frames

        # Add play and pause buttons with speed control
        fig.update_layout(
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': '▶️ Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 1000 // animation_speed, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 0}
                        }]
                    },
                    {
                        'label': '⏸️ Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ]
            }]
        )

        # Update layout for better visualization
        fig.update_layout(
            title="Animated Transaction Network",
            scene=dict(
                xaxis=dict(showticklabels=False, title=''),
                yaxis=dict(showticklabels=False, title=''),
                zaxis=dict(showticklabels=False, title=''),
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
            ),
            template="plotly_dark",
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0)
        )

        # Display the animated graph
        st.plotly_chart(fig, use_container_width=True)

        # Add transaction details below the graph
        st.subheader("Recent Transactions")
        for tx in transactions:
            with st.expander(f"Transaction {tx['signature'][:15]}..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**From:**", tx['from'][:20] + "...")
                    st.write("**To:**", tx['to'][:20] + "...")
                with col2:
                    st.write("**Amount:**", format_lamports(tx['amount']), "SOL")
                    st.write("**Time:**", format_timestamp(tx['timestamp']))

    except Exception as e:
        st.error("Error creating transaction visualization")
        st.error(f"Details: {str(e)}")