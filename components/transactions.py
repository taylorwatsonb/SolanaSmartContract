import streamlit as st
from utils.data_processing import format_timestamp, format_lamports

@st.cache_data(ttl=30)
def show_transactions(_client):
    st.header("💫 Recent Transactions")

    transactions = _client.get_recent_transactions(15)

    for tx in transactions:
        with st.expander(f"Transaction {tx['signature'][:15]}..."):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**From:**", tx['from'])
                st.write("**To:**", tx['to'])
            with col2:
                st.metric("Amount (SOL)", format_lamports(tx['amount']))
            with col3:
                st.write("**Status:**", "✅ Success" if tx['success'] else "❌ Failed")
                st.write("**Time:**", format_timestamp(tx['timestamp']))

def show_transaction_details(_client, signature):
    st.header("Transaction Details")

    tx = _client.get_transaction(signature)

    if tx:
        st.write("**Status:**", "✅ Success" if tx['success'] else "❌ Failed")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Signature:**", tx['signature'])
            st.write("**Block:**", tx['block'])
            st.write("**Timestamp:**", format_timestamp(tx['timestamp']))
        with col2:
            st.write("**From:**", tx['from'])
            st.write("**To:**", tx['to'])
            st.write("**Amount:**", format_lamports(tx['amount']), "SOL")

        # Show instruction details
        st.subheader("Instructions")
        for idx, instruction in enumerate(tx['instructions']):
            st.write(f"**Instruction {idx + 1}:**", instruction['program'])
            st.code(instruction['data'])