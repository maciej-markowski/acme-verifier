#!/usr/bin/python3

import os
import re

from netaddr import IPAddress, IPSet
from http.server import BaseHTTPRequestHandler, HTTPServer

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        request_headers = self.headers
        ipaddr = request_headers.get('X-Forwarded-For')
        if ipaddr is None:
            response = 400
            message = 'No X-Forwarded-For.'
        else:
            if verify(ipaddr):
                response = 200
                message = 'OK'
            else:
                response = 401
                message = 'Unauthorized'            

        self.send_response(response)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write(bytes(message, 'utf8'))

    def do_POST(self):
        request_headers = self.headers
        content_type = request_headers.get('Content-Type')
        if content_type != 'text/plain':
            response = 400
            message = 'Wrong content type. Post text/plain.'
        content_length = request_headers.get('Content-Length')
        if content_length is None:
            response = 400
            message = 'No content.'
        else:
            content = self.rfile.read(int(content_length))
            reg = re.compile(r'x-forwarded-for: (((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4})', flags=re.IGNORECASE|re.S)
            ipaddress = re.search(reg, content.decode('utf-8'))

            if ipaddress is None:
                response = 400
                message = 'No valid IP in x-forwarded-for'
            else:
                ipaddr = IPAddress(ipaddress.group(1))
                if verify(ipaddr):
                    response = 200
                    message = 'OK'
                else:
                    response = 401
                    message = 'Unauthorized'

        self.send_response(response)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write(bytes(message, 'utf8'))


def verify(ipaddr):
    ip_whitelist = os.environ.get('IP_WHITELIST', '/var/ranges/ip_whitelist.txt')
    with open(ip_whitelist) as file:
        whitelist = IPSet([line.rstrip() for line in file])

    if ipaddr in whitelist:
        return True
    return False


def main():
    PORT = os.environ.get('VERIFIER_PORT', 8080)
    with HTTPServer(('', PORT), handler) as server:
        server.serve_forever()


if __name__ == '__main__':
    main()
