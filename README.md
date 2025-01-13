# Solana Blockchain Explorer

An advanced blockchain explorer for the Solana network that provides comprehensive insights through interactive visualizations and analysis tools.

## Features

### 1. Network Statistics Dashboard
- Real-time network performance metrics
- TPS (Transactions Per Second) monitoring
- Active validator statistics
- Stake distribution visualization

### 2. Block Explorer
- Latest block information
- Detailed block analysis
- Transaction list within blocks
- Block hash and timestamp data

### 3. Transaction Monitoring
- Recent transaction tracking
- Detailed transaction analysis
- Status and confirmation tracking
- Fee calculation and display

### 4. Token Transfer Tracking
- SPL token transfer monitoring
- Token account management
- Transfer volume visualization
- Token holder analytics

### 5. Interactive 3D Transaction Graph
- Real-time transaction visualization
- Interactive 3D network graph
- Node relationship exploration
- Transaction flow analysis

### 6. Wallet Analytics
- Comprehensive wallet performance metrics
- Transaction history analysis
- Token holdings overview
- Activity pattern visualization

### 7. Learning Center
- Interactive blockchain tutorials
- Achievement badge system
- Progress tracking
- Gamified learning experience

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
SOLANA_RPC_ENDPOINT=your-rpc-endpoint
```

## Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Components

### Network Statistics (`components/network_stats.py`)
- Monitors and displays network performance metrics
- Visualizes TPS and validator statistics

### Block Explorer (`components/blocks.py`)
- Shows latest blocks and their details
- Provides block navigation and search

### Transaction Viewer (`components/transactions.py`)
- Displays recent transactions
- Provides detailed transaction analysis

### Token Transfers (`components/token_transfers.py`)
- Tracks SPL token movements
- Shows transfer patterns and volumes

### Wallet Analytics (`components/wallet_analytics.py`)
- Analyzes wallet performance
- Displays transaction history and patterns

### Transaction Graph (`components/transaction_graph.py`)
- Creates interactive 3D visualization
- Shows transaction relationships

### Learning Module (`components/learning_module.py`)
- Provides interactive blockchain lessons
- Implements achievement system

## Smart Contract Integration

The project includes a Solana token contract (`src/lib.rs`) that demonstrates:
- Token Account Management
- Safe Token Transfers
- Secure Account Initialization
- Comprehensive Error Handling

## Dependencies

- Python 3.11
- Streamlit
- Plotly
- Solana SDK
- NumPy
- Rust (for smart contracts)

## Development

The project follows a modular architecture with:
- Component-based UI structure
- Efficient data processing utilities
- Robust error handling
- Caching for performance optimization

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use and modify for your own projects.