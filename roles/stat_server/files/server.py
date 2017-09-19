from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse
import json

NODES = {}


class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(NODES))
        return

    def do_POST(self):
        content_len = int(self.headers.getheader('content-length'))
        post_body = self.rfile.read(content_len)
        self.send_response(200)
        self.end_headers()

        data = json.loads(post_body)

        NODES[data["id"]] = data
        self.wfile.write(data)
        return


if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('localhost', 8080), GetHandler)
    print 'Starting server at http://localhost:8080'
    server.serve_forever()
