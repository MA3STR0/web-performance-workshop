#!/usr/bin/env python

import os
import tornado.ioloop
import yaml
import json
from time import sleep
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.options import options, define
from tornado.netutil import bind_unix_socket
from tornado.httpserver import HTTPServer
from tornado.gen import coroutine

define('unix_socket', default="/tmp/nginx.socket", help='Path to unix socket to bind')
DEBUG = 'DYNO' not in os.environ


def query_cats():
    with open('database.yml') as yfile:
        cats = yaml.load(yfile)
    for cat in cats:
        sleep(0.05)
        yield cat


class CatStreamHandler(RequestHandler):
    @coroutine
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        for row in query_cats():
            self.write(json.dumps(row)+'\n')
            self.flush()
        self.finish()


class MainHandler(RequestHandler):
    def get(self):
        cats = list(query_cats())
        self.render("templates/index.html", cats=cats)


class CatlessHandler(RequestHandler):
    def get(self):
        self.render("templates/index.html", cats=[])

if __name__ == "__main__":
    app = Application(
        [
            (r"/", MainHandler),
            (r"/catless", CatlessHandler),
            (r"/catstream", CatStreamHandler),
            (r"/img/(.*)", StaticFileHandler, {'path': 'img'}),
            (r"/css/(.*)", StaticFileHandler, {'path': 'css'}),
            (r"/js/(.*)", StaticFileHandler, {'path': 'js'}),
            (r"/vendor/(.*)", StaticFileHandler, {'path': 'vendor'}),
        ], debug=DEBUG)
    if not DEBUG:
        server = HTTPServer(app)
        socket = bind_unix_socket(options.unix_socket)
        server.add_socket(socket)
        open('/tmp/app-initialized', 'w').close()
    else:
        port = os.environ.get("PORT", '8000')
        app.listen(port)
    tornado.ioloop.IOLoop.current().start()
