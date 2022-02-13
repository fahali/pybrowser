import socket


def request(url):
    HTTP = "http://"
    NEWLINE = "\r\n"
    ENCODING = "utf8"

    assert url.startswith(HTTP)
    url = url[len(HTTP) :]

    host, path = url.split("/", 1)
    path = "/" + path
    action = "GET {} HTTP/1.0{}".format(path, NEWLINE)
    request_header_host = "Host: {}".format(host)

    s = socket.socket(
        family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
    )
    s.connect((host, 80))

    s.send(action.encode(ENCODING) + request_header_host.encode(ENCODING))
    response = s.makefile("r", encoding=ENCODING, newline=NEWLINE)

    statusline = response.readline()
    _, status, explanation = statusline.split(" ", 2)
    assert status == "200", "{}: {}".format(status, explanation)

    headers = {}
    while True:
        line = response.readline()
        if line == NEWLINE:
            break
        header, value = line.split(":", 1)
        headers[header.lower()] = value.strip()

    body = response.read()
    s.close()

    return headers, body
