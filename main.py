from flask import (
    Flask,
    render_template
)
import requests
import logging

app = Flask(__name__)
@app.route('/', methods=["GET"])

def index():
    global requestedUrl, tag
    #TODO: Implement mechanism to get only opinions, not the whole site
    requestedUrl = 'https://www.ceneo.pl/94823130;02514?tag=producenci-philips#tab=reviews'
    tag = 'div'
    page = requests.get(requestedUrl)
    return page.text

if __name__ == '__main__':
    app.run(debug=True)