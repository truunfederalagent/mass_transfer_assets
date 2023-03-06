from algosdk.v2client import algod
from algosdk.transaction import AssetCloseOutTxn, AssetOptInTxn
from algosdk import mnemonic, account
import json


algod_client = algod.AlgodClient(algod_token='', algod_address='https://mainnet-api.algonode.cloud', headers={'User-Agent': 'py-algorand-sdk'})

with open('secrets.conf') as f:
    secrets = json.loads(f.read())

old_private_key = mnemonic.to_private_key(secrets['old_mnemonic'])
new_private_key = mnemonic.to_private_key(secrets['new_mnemonic'])

old_address = account.address_from_private_key(old_private_key)
new_address = account.address_from_private_key(new_private_key)

# Grab all assets from old account that can be transferred

assets = []
old_account_info = algod_client.account_info(old_address)

for asset in old_account_info['assets']:
    if not asset['is-frozen'] and asset['amount'] > 0:
        assets.append(asset['asset-id'])

# Opt in to all assets with new account

for asset in assets:
    sp = algod_client.suggested_params()
    sp.fee = 1000
    sp.flat_fee = True
    txn = AssetOptInTxn(
        sender=new_address,
        index=asset,
        sp=sp
    )
    stxn = txn.sign(new_private_key)
    algod_client.send_transaction(stxn)
    print('Opted', new_address, 'into', asset)

# Send all assets from old account to new account

for asset in assets:
    sp = algod_client.suggested_params()
    sp.fee = 1000
    sp.flat_fee = True
    txn = AssetCloseOutTxn(
        sender=old_address,
        receiver=new_address,
        index=asset,
        sp=sp
    )
    stxn = txn.sign(old_private_key)
    algod_client.send_transaction(stxn)
    print('Sent', asset, 'to', new_address)