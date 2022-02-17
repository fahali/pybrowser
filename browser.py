HTTP_SCHEME = "http"
HTTPS_SCHEME = "https"
FILE_SCHEME = "file"
SUPPORTED_SCHEMES = [HTTP_SCHEME, HTTPS_SCHEME, FILE_SCHEME]

NEWLINE = "\r\n"
READONLY = "r"


def parse_scheme(url):
    SCHEME_SEPARATOR = "://"

    scheme, url = url.split(SCHEME_SEPARATOR, 1)
    assert scheme in SUPPORTED_SCHEMES, f"Unknown scheme {scheme}"

    return scheme, url


def append_header(key, value, headers=""):
    return f"{headers}{key}: {value}{NEWLINE}"


def request(url):
    import socket
    import ssl

    HTTP_PROTOCOL_1_1 = "HTTP/1.1"
    METHOD_GET = "GET"
    STATUS_OK = "200"

    PATH_SEPARATOR = "/"
    PORT_SEPARATOR = ":"
    HEADER_SEPARATOR = " "
    HEADER_KEY_VALUE_SEPARATOR = ":"

    HTTP_PORT = 80
    HTTPS_PORT = 443
    ENCODING = "utf8"

    scheme, url = parse_scheme(url)

    # set a default port to start
    port = HTTP_PORT if scheme == HTTP_SCHEME else HTTPS_PORT

    host, path = url.split(PATH_SEPARATOR, 1)
    path = f"/{path}"  # replace the stripped path separator

    # get the correct port if it's available
    if PORT_SEPARATOR in host:
        host, port = host.split(PORT_SEPARATOR, 1)
        port = int(port)

    request_action = f"{METHOD_GET} /index.html {HTTP_PROTOCOL_1_1}{NEWLINE}"

    request_headers = append_header("Host", host)
    request_headers = append_header("Connection", "close", request_headers)
    request_headers = append_header("User-Agent", "pybrowser", request_headers)

    request = f"{request_action}{request_headers}{NEWLINE}".encode(ENCODING)

    tcp_socket = socket.socket(
        family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
    )
    tcp_socket.connect((host, port))

    if scheme == HTTPS_SCHEME:
        context = ssl.create_default_context()
        tcp_socket = context.wrap_socket(tcp_socket, server_hostname=host)

    tcp_socket.send(request)
    response = tcp_socket.makefile(READONLY, encoding=ENCODING, newline=NEWLINE)

    statusline = response.readline()
    version, status, explanation = statusline.split(HEADER_SEPARATOR, 2)
    assert status == STATUS_OK, f"{status}: {explanation}"

    headers = {}
    while True:
        line = response.readline()
        if line == NEWLINE:
            break
        header, value = line.split(HEADER_KEY_VALUE_SEPARATOR, 1)
        headers[header.lower()] = value.strip()  # normalize headers

    body = response.read()
    tcp_socket.close()

    return headers, body


def show(body):
    OPEN_TAG_CHARACTER = "<"
    CLOSE_TAG_CHARACTER = ">"

    in_html_tag = False
    for char in body:
        if char == OPEN_TAG_CHARACTER:
            in_html_tag = True
        elif char == CLOSE_TAG_CHARACTER:
            in_html_tag = False
        elif not in_html_tag:
            print(char, end="")


def print_file_contents(path):
    file = open(path, READONLY)
    contents = file.read()
    print(contents)


def load(url):
    scheme, path = parse_scheme(url)

    match scheme:
        case "http" | "https":
            headers, body = request(url)
            show(body)
        case "file":
            print_file_contents(path)


if __name__ == "__main__":
    import sys

    DEFAULT_FILE_PATH = "file://default.txt"

    if len(sys.argv) > 1:
        load(sys.argv[1])
    else:
        load(DEFAULT_FILE_PATH)
