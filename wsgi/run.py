import os
from flask import Flask, make_response
from decorators import crossdomain

app = Flask(__name__, static_folder='data', static_url_path='')

MODULE = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
def index():
    return "Nothing to see here."

@app.route("/<filename>.csv", methods=['GET', 'OPTIONS'])
@crossdomain(origin="*")
def csv_file(filename):
    with open(os.path.join(MODULE, 'data', filename + '.csv')) as fp:
        response = make_response(fp.read())
    response.headers['Content-type'] = 'text/csv'
    return response

if __name__ == '__main__':
    app.run(debug=False)
