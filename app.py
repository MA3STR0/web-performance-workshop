#!/usr/bin/env python

import os
import tornado.ioloop
import yaml
import json
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.options import options, define
from tornado.netutil import bind_unix_socket
from tornado.httpserver import HTTPServer
from tornado.gen import coroutine, sleep
from tornado.concurrent import Future

define('unix_socket', default="/tmp/nginx.socket", help='Path to unix socket to bind')
DEBUG = 'DYNO' not in os.environ


def query_cats():
    with open('database.yml') as yfile:
        cats = yaml.load(yfile)
    for cat in cats:
        yield sleep(0.5)
        yield cat


class CatStreamHandler(RequestHandler):
    @coroutine
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        for row in query_cats():
            if type(row) == Future:
                yield row
                continue
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
    port = os.environ.get("PORT", '8000')
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
