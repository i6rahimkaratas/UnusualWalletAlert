import requests
import json
import time

def get_btc_price_in_usd():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["bitcoin"]["usd"]
    except requests.exceptions.RequestException as e:
        print(f"Hata: Bitcoin fiyatı alınamadı - {e}")
        return None

def check_wallet_transactions(wallet_address, threshold_usd=100000):
    print(f"{wallet_address} adresi izleniyor...")
    last_tx_hash = None

    while True:
        try:
            btc_price_usd = get_btc_price_in_usd()
            if not btc_price_usd:
                time.sleep(60)
                continue

            url = f"https://blockchain.info/rawaddr/{wallet_address}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if not data['txs']:
                print("Bu cüzdanda henüz işlem bulunmuyor.")
                time.sleep(60)
                continue

            latest_tx = data['txs'][0]

            if last_tx_hash != latest_tx['hash']:
                last_tx_hash = latest_tx['hash']
                for tx_output in latest_tx['out']:
                    if 'addr' in tx_output and tx_output['addr'] == wallet_address:
                        amount_satoshi = tx_output['value']
                        amount_btc = amount_satoshi / 100000000
                        tx_value_usd = amount_btc * btc_price_usd

                        if tx_value_usd > threshold_usd:
                            print("\n--- BÜYÜK İŞLEM ALARMI ---")
                            print(f"İşlem Tipi: Para Yatırma")
                            print(f"Miktar: {amount_btc:.8f} BTC")
                            print(f"Değer: ${tx_value_usd:,.2f} USD")
                            print(f"İşlem Hash: {latest_tx['hash']}")
                            print("------------------------\n")

                for tx_input in latest_tx['inputs']:
                    if 'prev_out' in tx_input and 'addr' in tx_input['prev_out'] and tx_input['prev_out']['addr'] == wallet_address:
                        amount_satoshi = tx_input['prev_out']['value']
                        amount_btc = amount_satoshi / 100000000
                        tx_value_usd = amount_btc * btc_price_usd

                        if tx_value_usd > threshold_usd:
                            print("\n--- BÜYÜK İŞLEM ALARMI ---")
                            print(f"İşlem Tipi: Para Çekme")
                            print(f"Miktar: {amount_btc:.8f} BTC")
                            print(f"Değer: ${tx_value_usd:,.2f} USD")
                            print(f"İşlem Hash: {latest_tx['hash']}")
                            print("------------------------\n")

            time.sleep(60)

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 404:
                print("Hata: Belirtilen cüzdan adresi bulunamadı.")
                break
            else:
                print(f"HTTP Hatası: {http_err}")
                time.sleep(60)
        except requests.exceptions.RequestException as e:
            print(f"Bir hata oluştu: {e}")
            time.sleep(60)
        except KeyboardInterrupt:
            print("\nProgram sonlandırıldı.")
            break

if __name__ == "__main__":
    btc_address = "BURAYA_IZLENECEK_BITCOIN_ADRESINI_GIRIN"
    check_wallet_transactions(btc_address)
