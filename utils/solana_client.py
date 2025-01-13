from solana.rpc.api import Client
import datetime
import time
from solana.publickey import PublicKey
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SolanaClient:
    def __init__(self):
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=0.5,  # wait 0.5s * (2 ^ (retry - 1)) between retries
            status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)

        # Try multiple endpoints in case one is down
        self.endpoints = [
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com",
            "https://rpc.ankr.com/solana"
        ]
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Try to connect to available endpoints with proper configuration"""
        for endpoint in self.endpoints:
            try:
                temp_client = Client(endpoint, commitment='confirmed')
                # Configure the client with version support
                temp_client._provider.endpoint_opts = {
                    'maxSupportedTransactionVersion': 0
                }
                # Test the connection
                temp_client.get_slot()
                self.client = temp_client
                print(f"Connected to Solana network via {endpoint}")
                return
            except Exception as e:
                print(f"Failed to connect to {endpoint}: {str(e)}")
                continue

        # If all endpoints fail, use the first one as fallback
        self.client = Client(self.endpoints[0], commitment='confirmed')
        self.client._provider.endpoint_opts = {
            'maxSupportedTransactionVersion': 0
        }
        print("Warning: Using fallback endpoint. Some features might be unavailable.")

    def _handle_request(self, request_func, error_message):
        """Generic handler for RPC requests with retry logic and version handling"""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = request_func()
                if not response:
                    print(f"Empty response received")
                    retry_count += 1
                    continue

                if isinstance(response, dict) and 'error' in response:
                    if 'Transaction version' in str(response['error']):
                        # Update client configuration and retry
                        self.client._provider.endpoint_opts = {
                            'maxSupportedTransactionVersion': 0
                        }
                        retry_count += 1
                        continue

                return response.get('result') if isinstance(response, dict) else response

            except Exception as e:
                print(f"{error_message}: {str(e)}")
                retry_count += 1
                if retry_count >= max_retries:
                    # Try to reinitialize client on consistent failure
                    self._initialize_client()
                    return None
                continue

        return None

    def get_recent_blocks(self, limit=10):
        """Get recent blocks with improved error handling"""
        try:
            # Get current slot
            slot = self._handle_request(
                lambda: self.client.get_slot(),
                "Failed to get current slot"
            )
            if not slot:
                return []

            blocks = []
            for i in range(limit):
                try:
                    block = self._handle_request(
                        lambda: self.client.get_block(slot - i),
                        f"Error fetching block {slot - i}"
                    )
                    if block:
                        blocks.append({
                            'blocknumber': slot - i,
                            'blockhash': block['blockhash'],
                            'transactions': len(block['transactions']),
                            'timestamp': block.get('blockTime', int(time.time()))
                        })
                except Exception as block_error:
                    print(f"Error fetching block {slot - i}: {str(block_error)}")
                    continue

            return blocks
        except Exception as e:
            print(f"Error in get_recent_blocks: {str(e)}")
            return []

    def get_block(self, block_number):
        try:
            response = self._handle_request(lambda: self.client.get_block(block_number), f"Error fetching block {block_number}")
            if not response:
                return None
            block = response
            return {
                'blockhash': block['blockhash'],
                'parenthash': block['previousBlockhash'],
                'slot': block['parentSlot'],
                'timestamp': block.get('blockTime', 0),
                'transactions': len(block['transactions']),
                'leader': block['rewards'][0]['pubkey'] if block.get('rewards') else 'Unknown',
                'transaction_details': [
                    {
                        'signature': tx['transaction']['signatures'][0],
                        'success': 'err' not in tx['meta']
                    } for tx in block['transactions']
                ]
            }
        except Exception as e:
            print(f"Error in get_block: {str(e)}")
            return None

    def get_recent_transactions(self, limit=15):
        try:
            response = self._handle_request(lambda: self.client.get_recent_blockhash(), "Failed to get recent blockhash")
            if not response:
                return []

            signatures_response = self._handle_request(
                lambda: self.client.get_signatures_for_address(
                    response['blockhash'],
                    limit=limit
                ),
                "Failed to get signatures for address"
            )

            if not signatures_response:
                return []

            signatures = signatures_response
            transactions = []

            for sig in signatures:
                try:
                    tx_response = self._handle_request(lambda: self.client.get_transaction(sig['signature']), f"Error fetching transaction {sig['signature']}")
                    if tx_response:
                        tx = tx_response
                        transactions.append({
                            'signature': sig['signature'],
                            'from': tx['transaction']['message']['accountKeys'][0],
                            'to': tx['transaction']['message']['accountKeys'][1],
                            'amount': tx['meta']['postBalances'][1] - tx['meta']['preBalances'][1],
                            'success': 'err' not in tx['meta'],
                            'timestamp': tx.get('blockTime', 0)
                        })
                except Exception as tx_error:
                    print(f"Error processing transaction {sig['signature']}: {str(tx_error)}")
                    continue

            return transactions
        except Exception as e:
            print(f"Error in get_recent_transactions: {str(e)}")
            return []

    def get_network_stats(self):
        try:
            # Get epoch info
            epoch_info = self._handle_request(lambda: self.client.get_epoch_info(), "Failed to get epoch info")
            if not epoch_info:
                return None

            # Get validators
            validators = self._handle_request(lambda: self.client.get_vote_accounts(), "Failed to get validators info")
            if not validators:
                return None

            # Get recent blocks for TPS calculation
            recent_blocks = self.get_recent_blocks(30)
            if not recent_blocks:
                return None

            # Calculate TPS
            block_times = [block['timestamp'] for block in recent_blocks]
            total_transactions = sum(block['transactions'] for block in recent_blocks)
            time_span = max(block_times) - min(block_times) if block_times else 1
            current_tps = total_transactions / (time_span if time_span > 0 else 1)

            # Generate TPS history
            tps_history = {
                'timestamp': [
                    datetime.datetime.fromtimestamp(block['timestamp'])
                    for block in recent_blocks
                ],
                'tps': [
                    block['transactions'] for block in recent_blocks
                ]
            }

            # Get stake distribution
            current_validators = validators.get('current', [])
            stake_distribution = {
                'validators': [v['nodePubkey'][:10] for v in current_validators[:10]] if current_validators else [],
                'stakes': [v['activatedStake'] for v in current_validators[:10]] if current_validators else []
            }

            return {
                'current_slot': epoch_info['absoluteSlot'],
                'epoch': epoch_info['epoch'],
                'current_tps': current_tps,
                'active_validators': len(current_validators),
                'tps_history': tps_history,
                'stake_distribution': stake_distribution
            }
        except Exception as e:
            print(f"Error in get_network_stats: {str(e)}")
            return None

    def get_token_transfers(self, limit=20):
        """Fetch recent token transfer activities"""
        try:
            recent_txs = self._handle_request(lambda: self.client.get_signatures_for_address(self.client.get_recent_blockhash()['result']['value']['blockhash'], limit=limit), "Failed to get signatures for address")
            if not recent_txs:
                return []

            transfers = []
            for sig_info in recent_txs:
                try:
                    tx = self._handle_request(lambda: self.client.get_transaction(sig_info['signature'], encoding="jsonParsed"), f"Error fetching transaction {sig_info['signature']}")
                    if tx and 'transaction' in tx:
                        for inst in tx['transaction']['message']['instructions']:
                            if inst.get('program') == 'spl-token':
                                parsed_info = inst.get('parsed', {}).get('info', {})
                                transfers.append({
                                    'signature': sig_info['signature'],
                                    'from': parsed_info.get('source', 'Unknown'),
                                    'to': parsed_info.get('destination', 'Unknown'),
                                    'amount': parsed_info.get('amount', '0'),
                                    'token': parsed_info.get('mint', 'Unknown'),
                                    'timestamp': tx.get('blockTime', 0),
                                    'type': inst.get('parsed', {}).get('type', 'Unknown')
                                })
                except Exception as tx_error:
                    continue

            return transfers
        except Exception as e:
            print(f"Error in get_token_transfers: {str(e)}")
            return []

    def get_token_info(self, token_address):
        """Get information about a specific token"""
        try:
            account_info = self._handle_request(lambda: self.client.get_account_info(PublicKey(token_address), encoding="jsonParsed"), f"Error fetching account info for {token_address}")
            if not account_info:
                return None

            parsed_data = account_info['data'].get('parsed', {}).get('info', {})
            return {
                'address': token_address,
                'supply': parsed_data.get('supply', '0'),
                'decimals': parsed_data.get('decimals', 0),
                'mint_authority': parsed_data.get('mintAuthority'),
            }
        except Exception as e:
            print(f"Error in get_token_info: {str(e)}")
            return None

    def get_wallet_performance(self, wallet_address, tx_limit=50):
        """Analyze wallet performance and return comprehensive metrics"""
        try:
            # Get basic account info
            account_info = self._handle_request(lambda: self.client.get_account_info(PublicKey(wallet_address)), f"Error fetching account info for {wallet_address}")
            if not account_info:
                return None

            # Get recent transactions
            signatures = self._handle_request(lambda: self.client.get_signatures_for_address(PublicKey(wallet_address), limit=tx_limit), f"Error fetching transactions for {wallet_address}")
            if not signatures:
                return None

            transactions = []
            successful_txs = 0
            unique_dates = set()
            recent_activity = []

            for sig_info in signatures:
                try:
                    tx = self._handle_request(lambda: self.client.get_transaction(sig_info['signature'], encoding="jsonParsed"), f"Error fetching transaction {sig_info['signature']}")
                    if not tx:
                        continue

                    timestamp = tx.get('blockTime', 0)
                    unique_dates.add(datetime.datetime.fromtimestamp(timestamp).date())

                    tx_data = {
                        'signature': sig_info['signature'],
                        'timestamp': timestamp,
                        'amount': tx['meta']['postBalances'][0] - tx['meta']['preBalances'][0],
                        'success': 'err' not in tx['meta'],
                        'type': self._determine_transaction_type(tx)
                    }

                    transactions.append(tx_data)
                    if tx_data['success']:
                        successful_txs += 1

                    if len(recent_activity) < 5:  # Keep only 5 most recent activities
                        recent_activity.append(tx_data)

                except Exception as tx_error:
                    print(f"Error processing transaction {sig_info['signature']}: {str(tx_error)}")
                    continue

            # Get token holdings
            token_holdings = self._get_token_holdings(wallet_address)

            return {
                'balance': account_info['lamports'] if account_info else 0,
                'total_transactions': len(transactions),
                'success_rate': (successful_txs / len(transactions) * 100) if transactions else 0,
                'active_days': len(unique_dates),
                'transaction_history': sorted(transactions, key=lambda x: x['timestamp']),
                'token_holdings': token_holdings,
                'recent_activity': sorted(recent_activity, key=lambda x: x['timestamp'], reverse=True)
            }

        except Exception as e:
            print(f"Error in get_wallet_performance: {str(e)}")
            return None

    def _determine_transaction_type(self, tx):
        """Determine the type of transaction based on its contents"""
        try:
            if 'instructions' in tx['transaction']['message']:
                program_id = tx['transaction']['message']['instructions'][0]['programId']
                if program_id == '11111111111111111111111111111111':
                    return 'Transfer'
                elif program_id == 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA':
                    return 'Token Transaction'
                else:
                    return 'Program Interaction'
            return 'Unknown'
        except:
            return 'Unknown'

    def _get_token_holdings(self, wallet_address):
        """Get token holdings for a wallet"""
        try:
            token_accounts = self._handle_request(lambda: self.client.get_token_accounts_by_owner(PublicKey(wallet_address), {'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'}), f"Error fetching token accounts for {wallet_address}")
            if not token_accounts:
                return []

            holdings = []
            for account in token_accounts:
                parsed_data = account['account']['data']['parsed']['info']
                if float(parsed_data['tokenAmount']['amount']) > 0:
                    holdings.append({
                        'token_name': parsed_data['mint'][:8] + "...",
                        'amount': float(parsed_data['tokenAmount']['amount'])
                    })
            return holdings

        except Exception as e:
            print(f"Error in _get_token_holdings: {str(e)}")
            return []

    def get_balance(self, address):
        """Get the balance of a Solana address"""
        try:
            response = self._handle_request(
                lambda: self.client.get_balance(address),
                f"Error fetching balance for {address}"
            )
            return response['value'] if response else 0
        except Exception as e:
            print(f"Error in get_balance: {str(e)}")
            return 0

    def get_vote_accounts(self):
        """Get information about all vote accounts"""
        try:
            response = self._handle_request(
                lambda: self.client.get_vote_accounts(),
                "Error fetching vote accounts"
            )
            if not response:
                return {'current': [], 'delinquent': []}

            # Add activation epoch and last vote information
            for validator in response.get('current', []):
                validator['activationEpoch'] = validator.get('activationEpoch', 0)
                validator['lastVote'] = validator.get('lastVote', 0)

            return response
        except Exception as e:
            print(f"Error in get_vote_accounts: {str(e)}")
            return {'current': [], 'delinquent': []}