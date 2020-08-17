import argparse
from datetime import datetime
import json
import logging
import sys
from time import sleep
from bitcoinrpc.authproxy import AuthServiceProxy, EncodeDecimal

logger = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
out_hdlr.setLevel(logging.INFO)
logger.addHandler(out_hdlr)
logger.setLevel(logging.INFO)


def main(rpcuser, rpcpassword, rpcport=None, testnet=False, confs=None, out=None):
    confs = confs or 3
    if not isinstance(confs, list):
        confs = [confs]
    if rpcport is None:
        rpcport = 8332 if not testnet else 18332
    chain = "mainnet" if not testnet else "testnet"
    while True:
        rpc_connection = AuthServiceProxy(
            "http://{}:{}@127.0.0.1:{}".format(rpcuser, rpcpassword, rpcport)
        )
        for c in confs:
            res = rpc_connection.estimaterawfee(c)
            json_res = json.dumps(res, default=EncodeDecimal)
            res = (
                f"{datetime.now().isoformat()},{chain},estimaterawfee({c}),{json_res}\n"
            )
            if out is not None:
                with open("results.txt", "a") as out:
                    out.write(res)
            else:
                print(res, end="")
        logger.info("scraped")
        sleep(60)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rpcuser", required=True)
    parser.add_argument("--rpcpassword", required=True)
    parser.add_argument("--out", type=argparse.FileType("a"), default=None)
    parser.add_argument("--testnet", default=False, action="store_true")
    parser.add_argument("--confs", default=None)
    return parser.parse_args(sys.argv[1:])


if __name__ == "__main__":
    args = parse_arguments()
    if args.confs is not None:
        args.confs = list(map(int, args.confs.split(",")))
    main(**vars(args))
