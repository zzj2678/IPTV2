import os
from urllib.parse import urlparse


def update_m3u8_content(play_url: str, m3u8_content: str, is_proxy: bool = False) -> str:
    parsed_url = urlparse(play_url)
    port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
    domain_port = f"{parsed_url.hostname}:{port}"
    base_path = "/".join(parsed_url.path.split("/")[:-1])

    lines = m3u8_content.strip().splitlines()
    modified_lines = []

    PROXY_URL = os.getenv("PROXY_URL", "") if is_proxy else ""

    for line in lines:
        if line.startswith("#"):
            modified_lines.append(line)
            continue

        parsed_line_url = urlparse(line)

        if not parsed_line_url.netloc:
            if line.startswith("/"):
                base_path = ''

            modified_line = (
                f"{PROXY_URL}/data/{domain_port}{base_path}{line}"
                if is_proxy
                else f"{parsed_url.scheme}://{domain_port}{base_path}{line}"
            )
        else:
            modified_line = (
                f"{PROXY_URL}/data/{parsed_line_url.hostname}:{parsed_line_url.port or (443 if parsed_line_url.scheme == 'https' else 80)}{parsed_line_url.path}"
                if is_proxy
                else line
            )

        modified_lines.append(modified_line)

    return "\n".join(modified_lines)
