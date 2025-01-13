import streamlit as st
import plotly.graph_objects as go
from utils.data_processing import format_timestamp

@st.cache_data(ttl=60)
def show_blocks(_client):
    st.header("📦 Latest Blocks")

    blocks = _client.get_recent_blocks(10)

    # Create block list
    for block in blocks:
        with st.expander(f"Block #{block['blocknumber']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Transactions", block['transactions'])
            with col2:
                st.metric("Timestamp", format_timestamp(block['timestamp']))
            with col3:
                st.metric("Block Hash", block['blockhash'][:10] + "...")

def show_block_details(_client, block_number):
    st.header(f"Block #{block_number} Details")

    block = _client.get_block(block_number)

    if block:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Block Hash:**", block['blockhash'])
            st.write("**Previous Hash:**", block['parenthash'])
            st.write("**Timestamp:**", format_timestamp(block['timestamp']))
        with col2:
            st.write("**Transactions:**", block['transactions'])
            st.write("**Slot:**", block['slot'])
            st.write("**Leader:**", block['leader'])

        # Transaction list in block
        st.subheader("Transactions in this block")
        for tx in block['transaction_details']:
            st.write(f"Hash: {tx['signature']}")
            st.write(f"Status: {'✅ Success' if tx['success'] else '❌ Failed'}")
            st.divider()