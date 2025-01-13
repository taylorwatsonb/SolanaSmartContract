import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processing import format_timestamp, format_lamports

def show_wallet_analytics(_client, wallet_address=None):
    st.header("👛 Wallet Analytics")

    # Input for wallet address if not provided
    if not wallet_address:
        wallet_address = st.text_input(
            "Enter wallet address",
            placeholder="Enter Solana wallet address..."
        )

    if not wallet_address:
        st.info("Please enter a wallet address to view analytics.")
        return

    try:
        # Fetch wallet data
        wallet_data = _get_wallet_data(_client, wallet_address)

        if not wallet_data:
            st.warning("Could not fetch wallet data. Please verify the address and try again.")
            return

        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Balance (SOL)", format_lamports(wallet_data['balance']))
        with col2:
            st.metric("Total Transactions", wallet_data['total_transactions'])
        with col3:
            st.metric("Success Rate", f"{wallet_data['success_rate']:.1f}%")
        with col4:
            st.metric("Active Days", wallet_data['active_days'])

        # Transaction History Chart
        st.subheader("Transaction History")
        if len(wallet_data['transaction_history']) > 1:
            df = {
                'Time': [format_timestamp(tx['timestamp']) for tx in wallet_data['transaction_history']],
                'Amount': [format_lamports(tx['amount']) for tx in wallet_data['transaction_history']]
            }
            fig = px.line(df, x='Time', y='Amount', template="plotly_dark")
            fig.update_layout(title="Transaction Volume Over Time")
            st.plotly_chart(fig, use_container_width=True)

        # Token Holdings
        st.subheader("Token Holdings")
        if wallet_data['token_holdings']:
            fig = px.pie(
                values=[holding['amount'] for holding in wallet_data['token_holdings']],
                names=[holding['token_name'] for holding in wallet_data['token_holdings']],
                template="plotly_dark"
            )
            fig.update_layout(title="Token Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No token holdings found for this wallet.")

        # Recent Activity
        st.subheader("Recent Activity")
        for tx in wallet_data['recent_activity']:
            with st.expander(f"Transaction {tx['signature'][:15]}..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Type:**", tx['type'])
                    st.write("**Amount:**", format_lamports(tx['amount']), "SOL")
                with col2:
                    st.write("**Status:**", "✅ Success" if tx['success'] else "❌ Failed")
                    st.write("**Time:**", format_timestamp(tx['timestamp']))

    except Exception as e:
        st.error("Error analyzing wallet performance")
        st.error(f"Details: {str(e)}")

@st.cache_data(ttl=60)
def _get_wallet_data(_client, wallet_address):
    """Cached function to fetch wallet performance data"""
    return _client.get_wallet_performance(wallet_address)