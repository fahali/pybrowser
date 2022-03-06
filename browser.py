HTTP_SCHEME = "http"
HTTPS_SCHEME = "https"
FILE_SCHEME = "file"
STANDARD_SCHEMES = [HTTP_SCHEME, HTTPS_SCHEME, FILE_SCHEME]

# the following are *special* schemes that need specific handling
DATA_SCHEME = "data"
VIEW_SOURCE_SCHEME = "view-source"

# common flags to multiple functions
NEWLINE = "\r\n"
READONLY = "r"
EMPTY_STRING = ""

OPEN_TAG_CHARACTER = "<"
CLOSE_TAG_CHARACTER = ">"
OPEN_TAG_ENTITY = "&lt;"
CLOSE_TAG_ENTITY = "&gt;"


def parse_standard_scheme(url):
    SCHEME_SEPARATOR = "://"

    scheme, url = url.split(SCHEME_SEPARATOR, 1)
    assert scheme in STANDARD_SCHEMES, f"Unknown scheme {scheme}"

    return scheme, url


def parse_data_scheme(url):
    SCHEME_SEPARATOR = ":"
    MIME_TYPE_SEPARATOR = ","

    _, rest = url.split(SCHEME_SEPARATOR, 1)
    mime_type, content = rest.split(MIME_TYPE_SEPARATOR, 1)

    return mime_type, content


def parse_view_source_scheme(url):
    SCHEME_SEPARATOR = ":"
    _, url = url.split(SCHEME_SEPARATOR, 1)

    return url


def append_header(key, value, headers=EMPTY_STRING):
    return f"{headers}{key}: {value}{NEWLINE}"


def request(url):
    import socket
    import ssl

    HTTP_PROTOCOL_1_1 = "HTTP/1.1"
    METHOD_GET = "GET"
    STATUS_OK = "200"

    DEFAULT_PATH = "/index.html"

    PATH_SEPARATOR = "/"
    PORT_SEPARATOR = ":"
    HEADER_SEPARATOR = " "
    HEADER_KEY_VALUE_SEPARATOR = ":"

    HTTP_PORT = 80
    HTTPS_PORT = 443
    ENCODING = "utf8"

    scheme, url = parse_standard_scheme(url)

    # set a default port to start
    port = HTTP_PORT if scheme == HTTP_SCHEME else HTTPS_PORT

    host, path = url.split(PATH_SEPARATOR, 1)
    path = f"/{path}"  # replace the stripped path separator

    if path == PATH_SEPARATOR:
        path = DEFAULT_PATH

    # get the correct port if it's available
    if PORT_SEPARATOR in host:
        host, port = host.split(PORT_SEPARATOR, 1)
        port = int(port)

    request_action = f"{METHOD_GET} {path} {HTTP_PROTOCOL_1_1}{NEWLINE}"

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


# TODO F# 2022.02.21 - make view source GLOBAL flag
def show(body):
    OPEN_BODY_TAG = "<body>"
    CLOSE_BODY_TAG = "</body>"

    OPEN_ENTITY = "&"
    CLOSE_ENTITY = ";"

    in_html_tag = False
    in_body_tag = False
    in_html_entity = False

    current_tag = EMPTY_STRING
    current_entity = EMPTY_STRING

    for char in body:
        if char == OPEN_TAG_CHARACTER:
            in_html_tag = True
            current_tag += char

        elif char == CLOSE_TAG_CHARACTER:
            in_html_tag = False
            current_tag += char

            if current_tag == OPEN_BODY_TAG:
                in_body_tag = True

            elif current_tag == CLOSE_BODY_TAG:
                in_body_tag = False

            current_tag = EMPTY_STRING

        elif char == OPEN_ENTITY:
            in_html_entity = True
            current_entity = char

        elif char == CLOSE_ENTITY:
            in_html_entity = False
            current_entity += char

            if current_entity == OPEN_TAG_ENTITY:
                print(OPEN_TAG_CHARACTER, end=EMPTY_STRING)

            elif current_entity == CLOSE_TAG_ENTITY:
                print(CLOSE_TAG_CHARACTER, end=EMPTY_STRING)

            in_body_tag = True
            current_entity = EMPTY_STRING

        elif in_html_tag:
            current_tag += char

        elif in_html_entity:
            current_entity += char

        elif in_body_tag:
            print(char, end=EMPTY_STRING)


def get_file_contents(path):
    file = open(path, READONLY)
    contents = file.read()

    return contents


def entity_replace(char):
    if char == OPEN_TAG_CHARACTER:
        return OPEN_TAG_ENTITY
    elif char == CLOSE_TAG_CHARACTER:
        return CLOSE_TAG_ENTITY
    else:
        return char


def transform(body):
    return "".join(entity_replace(char) for char in body)


def load(url):
    if url.startswith(DATA_SCHEME):
        mime_type, content = parse_data_scheme(url)
        show(content)

    else:
        view_source_mode = False

        if url.startswith(VIEW_SOURCE_SCHEME):
            view_source_mode = True
            url = parse_view_source_scheme(url)

        scheme, path = parse_standard_scheme(url)

        headers = ""
        body = ""

        if scheme in [HTTP_SCHEME, HTTPS_SCHEME]:
            headers, body = request(url)
        else:
            body = get_file_contents(path)

        if view_source_mode:
            show(transform(body))
        else:
            show(body)


if __name__ == "__main__":
    import sys

    DEFAULT_FILE_PATH = "file://index.html"

    if len(sys.argv) > 1:
        load(sys.argv[1])

    else:
        load(DEFAULT_FILE_PATH)
