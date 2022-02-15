def request(url):
    import socket
    import ssl

    HTTP_SCHEME = "http"
    HTTPS_SCHEME = "https"
    HTTP_PROTOCOL_1_0 = "HTTP/1.0"
    METHOD_GET = "GET"
    STATUS_OK = "200"

    NEWLINE = "\r\n"
    PATH_SEPARATOR = "/"
    SCHEME_SEPARATOR = "://"
    PORT_SEPARATOR = ":"
    HEADER_SEPARATOR = " "
    HEADER_KEY_VALUE_SEPARATOR = ":"

    HTTP_PORT = 80
    HTTPS_PORT = 443
    ENCODING = "utf8"
    READONLY = "r"

    scheme, url = url.split(SCHEME_SEPARATOR, 1)
    assert scheme in [HTTP_SCHEME, HTTPS_SCHEME], f"Unknown scheme {scheme}"

    # set a default port to start
    port = HTTP_PORT if scheme == HTTP_SCHEME else HTTPS_PORT

    host, path = url.split(PATH_SEPARATOR, 1)
    path = f"/{path}"  # replace the stripped path separator

    # get the correct port if it's available
    if PORT_SEPARATOR in host:
        host, port = host.split(PORT_SEPARATOR, 1)
        port = int(port)

    request_action = f"{METHOD_GET} /index.html {HTTP_PROTOCOL_1_0}{NEWLINE}"
    request_header = f"Host: {host}{NEWLINE * 2}"
    request = request_action.encode(ENCODING) + request_header.encode(ENCODING)

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


def load(url):
    headers, body = request(url)
    show(body)


if __name__ == "__main__":
    import sys

    load(sys.argv[1])
