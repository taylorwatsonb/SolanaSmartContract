import streamlit as st
import plotly.express as px
from utils.data_processing import format_timestamp

@st.cache_data(ttl=30)
def show_token_transfers(_client):
    st.header("🔄 Token Transfers")

    try:
        transfers = _client.get_token_transfers()

        if not transfers:
            st.info("No recent token transfers found. This could be due to network connectivity or API limitations.")
            return

        # Display recent transfers
        st.subheader("Recent Token Transfers")

        for transfer in transfers:
            with st.expander(f"Transfer {transfer['signature'][:15]}..."):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**From:**", transfer['from'][:20] + "...")
                    st.write("**To:**", transfer['to'][:20] + "...")
                with col2:
                    st.write("**Token:**", transfer['token'][:15] + "...")
                    st.write("**Amount:**", transfer['amount'])
                with col3:
                    st.write("**Type:**", transfer['type'])
                    st.write("**Time:**", format_timestamp(transfer['timestamp']))

        # Create transfer volume chart
        if len(transfers) > 1:
            st.subheader("Transfer Volume Over Time")
            df = {
                'Time': [format_timestamp(t['timestamp']) for t in transfers],
                'Amount': [float(t['amount']) for t in transfers]
            }
            fig = px.line(df, x='Time', y='Amount', template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error("Error loading token transfers. Please try refreshing the page.")
        st.error(f"Details: {str(e)}")

def show_token_details(_client, token_address):
    """Display detailed information about a specific token"""
    try:
        token_info = _client.get_token_info(token_address)

        if not token_info:
            st.warning(f"Could not fetch information for token address: {token_address}")
            return

        st.subheader(f"Token Details: {token_address[:15]}...")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Supply:**", token_info['supply'])
            st.write("**Decimals:**", token_info['decimals'])
        with col2:
            st.write("**Mint Authority:**", 
                    token_info['mint_authority'][:20] + "..." if token_info['mint_authority'] else "None")

    except Exception as e:
        st.error(f"Error loading token details: {str(e)}")