#!/usr/bin/env python

import os
import tornado.ioloop
import yaml
from time import sleep
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.options import options, define

define('unix_socket', default="/tmp/nginx.socket", help='Path to unix socket to bind')
DEBUG = 'DYNO' not in os.environ

def query_cats():
    with open('database.yml') as yfile:
        cats = yaml.load(yfile)
    for cat in cats:
        sleep(0.05)
        yield cat

class MainHandler(RequestHandler):
    def get(self):
        cats = list(query_cats())
        self.render("templates/index.html", cats=cats)

if __name__ == "__main__":
    app = Application(
        [
            (r"/", MainHandler),
            (r"/img/(.*)", StaticFileHandler, {'path': 'img'}),
            (r"/css/(.*)", StaticFileHandler, {'path': 'css'}),
            (r"/js/(.*)", StaticFileHandler, {'path': 'js'}),
            (r"/vendor/(.*)", StaticFileHandler, {'path': 'vendor'}),
        ], debug=DEBUG)
    port = os.environ.get("PORT", '8000')
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
