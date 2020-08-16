import argparse
import json
import sys

from bit import PrivateKeyTestnet
from bit.network.meta import Unspent
from bitcoinrpc.authproxy import AuthServiceProxy


def create_transactions(node1, node2, conn, original_tx, n):
    sender = node1
    receiver = node2
    raw_tx = conn.getrawtransaction(original_tx)
    last_tx = conn.decoderawtransaction(raw_tx)
    txs = []
    for i in range(n):
        txindex = [
            i
            for i, out in enumerate(last_tx["vout"])
            if out["scriptPubKey"]["addresses"][0] == sender.address
        ][0]
        incoming_value = int(float(last_tx["vout"][txindex]["value"]) * 10 ** 8)
        fee = 192 if i < n - 1 else incoming_value - 1
        transaction_value = incoming_value - fee
        txs += [
            sender.create_transaction(
                outputs=[(receiver.address, transaction_value, "satoshi")],
                unspents=[
                    Unspent(
                        amount=int(float(last_tx["vout"][txindex]["value"]) * 10 ** 8),
                        confirmations=0,
                        script=last_tx["vout"][txindex]["scriptPubKey"]["hex"],
                        txindex=0,
                        txid=last_tx["txid"],
                        segwit="p2pkh",
                    )
                ],
                fee=fee,
                absolute_fee=True,
            )
        ]
        sender, receiver = receiver, sender
        last_tx = conn.decoderawtransaction(txs[-1])
    return txs


def main(
    wif1, wif2, rpcuser, rpcpassword, num_transactions, original_tx, dry_run=False
):
    rpc_connection = AuthServiceProxy(
        "http://%s:%s@127.0.0.1:18332" % (rpcuser, rpcpassword)
    )
    txs = create_transactions(
        PrivateKeyTestnet(wif1),
        PrivateKeyTestnet(wif2),
        rpc_connection,
        original_tx,
        num_transactions,
    )
    if dry_run:
        res = rpc_connection.testmempoolaccept([txs[0]])
        print(json.dumps(res, indent=2))
    else:
        for tx in txs:
            rpc_connection.sendrawtransaction(tx, 0)
    print("\n".join(txs))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wif1", required=True)
    parser.add_argument("--wif2", required=True)
    parser.add_argument("--rpcuser", required=True)
    parser.add_argument("--rpcpassword", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("num_transactions", type=int)
    parser.add_argument("original_tx")
    return parser.parse_args(sys.argv[1:])


if __name__ == "__main__":
    args = parse_arguments()
    main(**vars(args))
