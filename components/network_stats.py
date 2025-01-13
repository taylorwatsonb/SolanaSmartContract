import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.data_processing import format_lamports
from utils.tooltips import show_tooltip, add_tooltip_style

@st.cache_data(ttl=60)
def show_network_stats(_client):
    st.header("📊 Network Statistics")
    add_tooltip_style()

    try:
        # Fetch network stats
        stats = _client.get_network_stats()

        if not stats:
            st.error("Unable to fetch network statistics. The Solana network might be experiencing issues.")
            return

        # Display key metrics with tooltips
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            show_tooltip("Slot")
            st.metric("Current Slot", stats['current_slot'])
        with col2:
            show_tooltip("TPS")
            st.metric("TPS", f"{stats['current_tps']:.2f}")
        with col3:
            show_tooltip("Epoch")
            st.metric("Epoch", stats['epoch'])
        with col4:
            show_tooltip("Validator")
            st.metric("Active Validators", stats['active_validators'])

        # TPS Chart
        st.subheader("Transaction Per Second (TPS)")
        if len(stats['tps_history']['timestamp']) > 0:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=stats['tps_history']['timestamp'],
                y=stats['tps_history']['tps'],
                mode='lines',
                name='TPS'
            ))
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Transactions per Second",
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No TPS history data available")

        # Stake Distribution
        if len(stats['stake_distribution']['stakes']) > 0:
            show_tooltip("Stake")
            st.subheader("Stake Distribution")
            fig = px.pie(
                values=stats['stake_distribution']['stakes'],
                names=stats['stake_distribution']['validators'],
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No stake distribution data available")

    except Exception as e:
        st.error("Error loading network statistics")
        st.error("Please try refreshing the page or check if the Solana network is accessible.")
        print(f"Error in show_network_stats: {str(e)}")