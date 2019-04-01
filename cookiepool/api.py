from flask import Flask, g
import json

from .db import DbClient

__all__ = ['app']

app = Flask(__name__)

def get_conn():
    if not hasattr(g, 'mongo'):
        g.db = DbClient()
    return g.db

@app.route('/')
def index():
    return '<h2> Welcome to cookies pool! <h2>'

@app.route('/get')
def get_proxy():
    conn = get_conn()
    return json.dumps(conn.get_requests_cookie())


