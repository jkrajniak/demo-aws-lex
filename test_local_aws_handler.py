import argparse
import http.server
import json
import os
import importlib

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def _args():
    parser = argparse.ArgumentParser('Local handler for LAMBDA requests')
    parser.add_argument('--port', default=3451, type=int, required=True)
    parser.add_argument('--module', default='', required=True)
    parser.add_argument('--handler', default='', required=True)
    parser.add_argument('--stage', default='dev2')
    return parser


class Handler(http.server.BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # Gets the size of data
        post_data = self.rfile.read(content_length)  # Gets the data itself

        input_json = json.loads(post_data.decode('utf-8'))
        output = handler(input_json, '')
        self._set_response()
        self.wfile.write(json.dumps(output).encode('utf-8'))


class FSHandler(FileSystemEventHandler):
    """"Reload the module whenever the file changes."""
    def on_modified(self, event):
        exec('{module} = importlib.reload({module})'.format(module=self.args.module), locals(), globals())
        exec('handler = {}.{}'.format(self.args.module, self.args.handler), locals(),
             globals())
        print('reload')


def main():
    args = _args().parse_args()

    # Load handler
    exec('import {}'.format(args.module), locals(), globals())
    exec('handler = {}.{}'.format(args.module, args.handler), locals(), globals())

    observer = Observer()
    fs_handler = FSHandler()
    fs_handler.args = args
    observer.schedule(fs_handler, '.', recursive=False)
    observer.start()

    httpd = http.server.HTTPServer(('', args.port), Handler)
    print('Running http server')

    httpd.serve_forever()


if __name__ == '__main__':
    main()
