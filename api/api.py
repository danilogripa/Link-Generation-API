import build
import flask
from flask import request

from build import build

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/convert', methods=['POST'])
def api_test():
    request_data = request.get_json()
    return build(request_data['red'], request_data['af'], request_data['tg'], request_data['key'], request_data['os'], request_data['ag'],
                 request_data['type'])


app.run(host="0.0.0.0")
