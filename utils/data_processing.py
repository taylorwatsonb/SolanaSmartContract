from datetime import datetime

def format_timestamp(timestamp):
    """Convert Unix timestamp to human-readable format"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def format_lamports(lamports):
    """Convert lamports to SOL"""
    return lamports / 1_000_000_000
