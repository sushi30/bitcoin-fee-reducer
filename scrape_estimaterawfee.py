import argparse
from datetime import datetime
import json
import logging
import sys
from time import sleep
from bitcoinrpc.authproxy import AuthServiceProxy, EncodeDecimal

logger = logging.getLogger(f"{__package__}.{__name__}")
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
out_hdlr.setLevel(logging.INFO)
logger.addHandler(out_hdlr)
logger.setLevel(logging.INFO)


def main(
    rpcuser,
    rpcpassword,
    rpcconnect="127.0.0.1",
    rpcport=None,
    testnet=False,
    confs=None,
    out=None,
):
    confs = confs or 3
    if not isinstance(confs, list):
        confs = [confs]
    if rpcport is None:
        rpcport = 8332 if not testnet else 18332
    chain = "mainnet" if not testnet else "testnet"
    while True:
        rpc_connection = AuthServiceProxy(
            "http://{}:{}@{}:{}".format(rpcuser, rpcpassword, rpcconnect, rpcport)
        )
        for c in confs:
            res = rpc_connection.estimaterawfee(c)
            res = json.dumps(
                {
                    "date": datetime.now().isoformat(),
                    "command": f"estimaterawfee({c})",
                    "chain": chain,
                    "data": res,
                },
                default=EncodeDecimal,
            )
            if out is not None:
                out.write(res + "\n")
                out.flush()
            else:
                print(res, end="")
        logger.info("scraped")
        sleep(60)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rpcuser", required=True)
    parser.add_argument("--rpcpassword", required=True)
    parser.add_argument("--rpcconnect", default="127.0.0.1")
    parser.add_argument("--out", type=argparse.FileType("a"), default=None)
    parser.add_argument("--testnet", default=False, action="store_true")
    parser.add_argument("--confs", default=None)
    return parser.parse_args(sys.argv[1:])


if __name__ == "__main__":
    args = parse_arguments()
    if args.confs is not None:
        args.confs = list(map(int, args.confs.split(",")))
    main(**vars(args))
