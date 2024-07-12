import os
from urllib.parse import urljoin, urlparse


def update_m3u8_content(play_url: str, m3u8_content: str, is_proxy: bool = False) -> str:
    parsed_url = urlparse(play_url)
    port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
    domain_port = f"{parsed_url.hostname}:{port}"

    base_url = f"{parsed_url.scheme}://{domain_port}"
    base_path = parsed_url.path.rsplit('/', 1)[0] + '/'

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

            if is_proxy:
                modified_line = f"{PROXY_URL}/data/" + domain_port + base_path + line
            else:
                modified_line = urljoin(base_url + base_path, line)
        else:
            if is_proxy:
                parsed_line_url = urlparse(line)
                line_port = parsed_line_url.port or (443 if parsed_line_url.scheme == 'https' else 80)
                line_domain_port = f"{parsed_line_url.hostname}:{line_port}"
                modified_line = urljoin(f"{PROXY_URL}/data/{line_domain_port}", parsed_line_url.path)
                if parsed_line_url.query:
                    modified_line += f"?{parsed_line_url.query}"
            else:
                modified_line = line

        modified_lines.append(modified_line)

    return "\n".join(modified_lines)
