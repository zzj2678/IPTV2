import argparse
import asyncio
import logging

from iptv.jiudian import JiuDian
from iptv.udpxy import UDPxy

logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(description="IP fetching and playlist generation script")
    parser.add_argument("--ip", action="store_true", help="Fetch valid IPs")
    parser.add_argument("--playlist", action="store_true", help="Generate playlists from valid IPs")
    parser.add_argument("--type", choices=["jiudian", "udpxy"], required=True, help="Type of IP to process")
    args = parser.parse_args()

    if args.ip:
        if args.type == "jiudian":
            await JiuDian().sniff_ip()
        elif args.type == "udpxy":
            await UDPxy().sniff_ip()
    elif args.playlist:
        if args.type == "jiudian":
            await JiuDian().generate_playlist()
        elif args.type == "udpxy":
            await UDPxy().generate_playlist()
    else:
        logging.error("You must specify an action: --ip or --playlist.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    asyncio.run(main())
