import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils.data_processing import format_timestamp
import networkx as nx

def create_network_topology(_client):
    """Create an animated visualization of the Solana network topology"""
    st.header("🌐 Network Topology")

    try:
        with st.spinner("Fetching network data..."):
            # Fetch validator information
            validators = _client.get_vote_accounts()
            if not validators or not validators.get('current'):
                st.warning("No validator information available. The network might be experiencing issues.")
                return

            # Create network graph
            G = nx.Graph()

            # Add nodes (validators)
            for validator in validators['current']:
                try:
                    stake = int(validator.get('activatedStake', 0))
                    G.add_node(
                        validator['nodePubkey'],
                        stake=stake,
                        delinquent=validator.get('delinquent', False),
                        last_vote=validator.get('lastVote', 0)
                    )
                except (KeyError, ValueError) as e:
                    print(f"Error adding validator node: {str(e)}")
                    continue

            if len(G.nodes()) == 0:
                st.warning("No active validators found in the network.")
                return

            # Calculate node positions using spring layout with error handling
            try:
                pos = nx.spring_layout(G, k=2, iterations=50)
            except Exception as e:
                print(f"Error in spring layout: {str(e)}")
                # Fallback to circular layout if spring layout fails
                pos = nx.circular_layout(G)

            # Prepare node data
            node_x = []
            node_y = []
            node_colors = []
            node_sizes = []
            node_texts = []

            max_stake = max(G.nodes[node]['stake'] for node in G.nodes())
            min_size = 10
            max_size = 50

            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)

                # Color based on status (delinquent vs active)
                node_colors.append('#FF3B3B' if G.nodes[node]['delinquent'] else '#00FF94')

                # Size based on stake (normalized)
                stake = G.nodes[node]['stake']
                normalized_size = min_size + (stake / max_stake) * (max_size - min_size)
                node_sizes.append(normalized_size)

                # Hover text with detailed information
                node_texts.append(
                    f"Validator: {node[:10]}...<br>"
                    f"Stake: {stake/1e9:.2f} SOL<br>"
                    f"Status: {'Delinquent' if G.nodes[node]['delinquent'] else 'Active'}<br>"
                    f"Last Vote: {format_timestamp(G.nodes[node]['last_vote'])}"
                )

            # Create figure
            fig = go.Figure()

            # Add edges with gradient effect
            edge_x = []
            edge_y = []
            for (node1, node2) in G.edges():
                x0, y0 = pos[node1]
                x1, y1 = pos[node2]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            fig.add_trace(go.Scatter(
                x=edge_x,
                y=edge_y,
                mode='lines',
                line=dict(
                    width=1,
                    color='rgba(153, 69, 255, 0.5)'  # Semi-transparent purple
                ),
                hoverinfo='none'
            ))

            # Add nodes with enhanced visual effects
            fig.add_trace(go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers',
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(width=2, color='#FFFFFF'),
                    symbol='circle',
                ),
                text=node_texts,
                hoverinfo='text'
            ))

            # Update layout for better visualization
            fig.update_layout(
                title="Solana Network Topology",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                updatemenus=[{
                    'type': 'buttons',
                    'showactive': False,
                    'buttons': [{
                        'label': '🔄 Refresh',
                        'method': 'relayout',
                        'args': ['xaxis.autorange', True]
                    }]
                }]
            )

            # Display the network topology
            st.plotly_chart(fig, use_container_width=True)

            # Show network statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Active Validators",
                    len([n for n in G.nodes() if not G.nodes[n]['delinquent']])
                )
            with col2:
                total_stake = sum(G.nodes[n]['stake'] for n in G.nodes())
                st.metric("Total Stake", f"{total_stake/1e9:.2f} SOL")
            with col3:
                avg_stake = total_stake / len(G.nodes()) if G.nodes else 0
                st.metric("Average Stake", f"{avg_stake/1e9:.2f} SOL")

    except Exception as e:
        st.error("Error creating network topology visualization")
        st.error(f"Details: {str(e)}")
        print(f"Error in create_network_topology: {str(e)}")