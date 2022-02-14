def request(url):
    import socket

    HTTP_PROTOCOL_1_0 = "HTTP/1.0"
    HTTP_PREFIX = "http://"
    DEFAULT_PATH = "/index.html"
    METHOD_GET = "GET"
    STATUS_OK = "200"

    NEWLINE = "\r\n"
    EMPTY_STRING = ""
    PATH_SEPARATOR = "/"
    HEADER_SEPARATOR = " "
    HEADER_KEY_VALUE_SEPARATOR = ":"

    HTTP_PORT = 80
    ENCODING = "utf8"
    READONLY = "r"

    assert url.startswith(HTTP_PREFIX)  # confirm HTTP protocol
    url = url[len(HTTP_PREFIX) :]  # discard the prefix

    host, path = url.split(PATH_SEPARATOR, 1)
    path = f"/{path}"  # replace the stripped path separator

    request_action = f"{METHOD_GET} /index.html {HTTP_PROTOCOL_1_0}{NEWLINE}"
    request_header = f"Host: {host}{NEWLINE * 2}"
    request = request_action.encode(ENCODING) + request_header.encode(ENCODING)

    tcp_socket = socket.socket(
        family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
    )
    tcp_socket.connect((host, HTTP_PORT))

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
