import streamlit as st

# Dictionary of blockchain terms and their explanations
BLOCKCHAIN_TERMS = {
    "TPS": "Transactions Per Second - The number of transactions that a blockchain can process each second.",
    "Slot": "A period of time in which a validator can produce a block.",
    "Epoch": "A period of time in which a particular set of validators is active.",
    "Validator": "A node that participates in the consensus process by validating and adding new blocks to the blockchain.",
    "Lamports": "The smallest unit of SOL (Solana's native token). 1 SOL = 1,000,000,000 lamports.",
    "Block Hash": "A unique identifier for a block, created by applying a hash function to the block's contents.",
    "Transaction Signature": "A cryptographic proof that authorizes a transaction, created using the sender's private key.",
    "SPL Token": "Solana Program Library Token - A token created using Solana's token program standard.",
    "Program ID": "The unique identifier of a smart contract (program) on the Solana blockchain.",
    "Stake": "The amount of SOL that validators and delegators bond to participate in consensus.",
    "RPC Node": "Remote Procedure Call Node - An endpoint that allows applications to interact with the Solana blockchain."
}

def show_tooltip(term: str, container=None):
    """Display a tooltip for a blockchain term"""
    if container is None:
        container = st

    if term in BLOCKCHAIN_TERMS:
        container.markdown(
            f"""
            <div class="tooltip">
                {term}
                <span class="tooltiptext">{BLOCKCHAIN_TERMS[term]}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        container.write(term)

def add_tooltip_style():
    """Add CSS styling for tooltips"""
    st.markdown(
        """
        <style>
        .tooltip {
            position: relative;
            display: inline-block;
            border-bottom: 1px dotted #9945FF;
            color: #FAFAFA;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 300px;
            background-color: #262730;
            color: #FAFAFA;
            text-align: center;
            border: 1px solid #9945FF;
            border-radius: 6px;
            padding: 8px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -150px;
            opacity: 0;
            transition: opacity 0.3s;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
