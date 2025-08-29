from json import dumps
from pathlib import Path

import requests


def validate_proxies(limit: int = 10) -> None:
    session = requests.Session()

    proxy_file = (Path(__file__).parent / "proxies.txt").read_text().split()
    proxies = [line.strip() for line in proxy_file if line.strip()]

    valid_proxies = []
    for proxy in proxies:
        if len(valid_proxies) == limit:
            break
        try:
            response = requests.get(
                "http://httpbin.org/ip",
                proxies={"https": proxy},
                timeout=3,
            )
            response.raise_for_status()
            valid_proxies.append(proxy)
        except requests.ReadTimeout:
            continue

    valid_proxy_file = Path(__file__).parent / "proxies.json"
    valid_proxy_file.write_text(dumps(valid_proxies, indent=2))

    session.close()


if __name__ == "__main__":
    validate_proxies()
