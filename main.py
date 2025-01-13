import streamlit as st
from components import (
    blocks, transactions, network_stats, token_transfers, 
    wallet_analytics, transaction_graph, learning_module, 
    network_topology
)
from utils.solana_client import SolanaClient

st.set_page_config(
    page_title="Taylor's Solana Explorer",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🌟 Taylor's Solana Blockchain Explorer")

    # Initialize Solana client
    client = SolanaClient()

    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select a page",
        ["Network Stats", "Network Topology", "Blocks", "Transactions", "Token Transfers", 
         "Wallet Analytics", "Transaction Graph", "Learning Center"]
    )

    # Search box
    search_query = st.text_input(
        "🔍 Search by block, transaction, token, or account address",
        placeholder="Enter hash or address..."
    )

    if search_query:
        try:
            if len(search_query) == 44:  # Account or transaction
                st.write("Searching for:", search_query)
                if search_query.startswith("So"):  # Token mint address
                    token_transfers.show_token_details(client, search_query)
                else:
                    # Check if it's a wallet address
                    if page == "Wallet Analytics":
                        wallet_analytics.show_wallet_analytics(client, search_query)
                    else:
                        transactions.show_transaction_details(client, search_query)
            elif search_query.isdigit():  # Block number
                blocks.show_block_details(client, int(search_query))
            else:
                st.error("Invalid search query format")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # Main content
    if page == "Network Stats":
        network_stats.show_network_stats(client)
    elif page == "Network Topology":
        network_topology.create_network_topology(client)
    elif page == "Blocks":
        blocks.show_blocks(client)
    elif page == "Transactions":
        transactions.show_transactions(client)
    elif page == "Token Transfers":
        token_transfers.show_token_transfers(client)
    elif page == "Transaction Graph":
        transaction_graph.create_transaction_graph(client)
    elif page == "Learning Center":
        learning_module.show_learning_module()
    else:
        wallet_analytics.show_wallet_analytics(client)

if __name__ == "__main__":
    main()