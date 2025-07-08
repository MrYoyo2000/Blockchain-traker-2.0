import requests
import time
import pandas as pd
import matplotlib.pyplot as plt

# === Clés API ===
ETHERSCAN_API_KEY = "VZFDUWB3YGQ1YCDKTCU1D6DDSS"
SOLANAFM_API_KEY = ""

class WalletTracker:
    def __init__(self, eth_api_key=None, sol_api_key=None):
        self.eth_api_key = eth_api_key
        self.sol_api_key = sol_api_key
        self.eth_wallet = []
        self.sol_wallet = []
        self.btc_wallet = []

    def add_wallet(self, address, blockchain="ETH"):
        blockchain = blockchain.upper()
        if blockchain == "ETH":
            self.eth_wallet.append(address)
        elif blockchain == "SOL":
            self.sol_wallet.append(address)
        elif blockchain == "BTC":
            self.btc_wallet.append(address)

    def get_eth_transactions(self, address):
        url = "https://api.etherscan.io/api"
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "desc",
            "apikey": self.eth_api_key
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"ETH API error: {response.status_code}")
            return []
        try:
            return response.json().get("result", [])
        except Exception as e:
            print(f"Erreur JSON ETH: {e}")
            return []


    def get_btc_transactions(self, address):
        url = f"https://blockstream.info/api/address/{address}/txs"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"BTC API error: {response.status_code}")
            return []
        try:
            return response.json()
        except Exception as e:
            print(f"Erreur JSON BTC: {e}\nContenu brut: {response.text[:200]}")
            return []

    def get_solana_transactions(self, address):
        url = f"https://api.solana.fm/v0/accounts/{address}/transactions"
        headers = {
            "Authorization": f"Bearer {self.sol_api_key}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Solana API error: {response.status_code}")
            return []
        try:
            return response.json().get("data", [])
        except Exception as e:
            print(f"Erreur JSON Solana: {e}")
            return []

    def display_big_transactions(self, transactions, min_value=100):
        rows = []
        for tx in transactions:
            if "value" in tx:  # Ethereum
                try:
                    value = int(tx["value"]) / 10**18
                    if value >= min_value:
                        rows.append({
                            "blockchain": "Ethereum",
                            "from": tx.get("from"),
                            "to": tx.get("to"),
                            "value": value,
                            "hash": tx.get("hash")
                        })
                except:
                    continue
            elif "lamports" in tx:  # Solana
                try:
                    value = int(tx["lamports"]) / 10**9
                    if value >= min_value:
                        rows.append({
                            "blockchain": "Solana",
                            "from": tx.get("sender", ""),
                            "to": tx.get("receiver", ""),
                            "value": value,
                            "txid": tx.get("signature", "")
                        })
                except:
                    continue

        if rows:
            df = pd.DataFrame(rows)
            print(df)
        else:
            print("Aucune grosse transaction ETH/SOL trouvée.")

    def display_btc_big_transactions(self, transactions, min_btc=1):
        rows = []
        for tx in transactions:
            try:
                if "vout" in tx:
                    total_out = sum(vout.get("value", 0) for vout in tx["vout"])
                    btc_value = total_out / 10**8
                    if btc_value >= min_btc:
                        rows.append({
                            "blockchain": "Bitcoin",
                            "txid": tx.get("txid", ""),
                            "value BTC": btc_value
                        })
            except:
                continue

        if rows:
            df = pd.DataFrame(rows)
            print(df)
        else:
            print("Aucune grosse transaction BTC trouvée.")

# === Utilisation ===
if __name__ == "__main__":
    tracker = WalletTracker(eth_api_key=ETHERSCAN_API_KEY, sol_api_key=SOLANAFM_API_KEY)

    # Remplace les adresses suivantes par de vraies adresses pour test réel
    tracker.add_wallet("0xceB69F6342eCE283b2F5c9088Ff249B5d0Ae66ea", blockchain="eth")
    tracker.add_wallet("BRicpav9aLPEbP6dVXyJZgY5i3vx3rktTTcLCtLjsvUm", blockchain="sol")
    tracker.add_wallet("3MqUP6G1daVS5YTD8fz3QgwjZortWwxXFd", blockchain="btc")

    while True:
        print("\n--- Analyse ETH ---")
        for addr in tracker.eth_wallet:
            txs = tracker.get_eth_transactions(addr)
            tracker.display_big_transactions(txs, min_value=1)

        print("\n--- Analyse SOL ---")
        for addr in tracker.sol_wallet:
            txs = tracker.get_solana_transactions(addr)
            tracker.display_big_transactions(txs, min_value=1)

        print("\n--- Analyse BTC ---")
        for addr in tracker.btc_wallet:
            txs = tracker.get_btc_transactions(addr)
            tracker.display_btc_big_transactions(txs, min_btc=1)

        print("\nAttente 30 secondes...")
        time.sleep(30)