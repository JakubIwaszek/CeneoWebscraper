from re import A
from flask import (
    Flask,
    flash,
    render_template,
    redirect,
    request,
    send_file
)
import requests
import logging
import json
import os
import pandas as pd
from Product import ProductDetails
import Review as Review
from functions import getProductData, getProductsFromJsons, saveProductAsJson
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
    return render_template("homepage.html")

@app.route('/extract', methods=["POST", "GET"])
def extractOpinions():
    error = None
    if request.method == "POST":
        productId = request.form['productId']
        redirectUrl = f'https://www.ceneo.pl/{productId}/'
        statusCode = requests.get(redirectUrl).status_code
        if len(productId) < 1:
            error = "Pole id produktu nie moze być puste."
        elif statusCode != 200:
            error = "Produkt o podanym id nie istnieje, lub wystąpił inny błąd."
        else:
            product = getProductData(productId)
            saveProductAsJson(product)
            return redirect(redirectUrl, code=302)
    return render_template("extractOpinion.html", error=error)

@app.route('/list', methods=["GET"])
def showProductsList():
    products = getProductsFromJsons()
    return render_template("productsList.html", variable=products)

@app.route("/download/<id>/<type>")
def download(id, type):
    file = pd.read_json(f'products/{id}.json')
    if type == "csv":
        app.logger.info("csv")
        file.to_csv('output/output.csv', index=False)
    elif type == "xlsx":
        file.to_excel('output/output.xlsx', index=False)
    else:
        return send_file(f'products/{id}.json')
    return send_file(f'output/output.{type}', download_name=f'{id}.{type}')

@app.route("/charts/<productId>")
def showCharts(productId):
     with open(os.path.join('products', f"{productId}.json"), "r") as file:
        product = json.load(file)
        recs = {'Title': 'Rekomendacje', 'Polecam': 0, 'Nie Polecam': 0}
        rating = { 'Ocena': 'Liczba Opinii', '0': 0, '0,5': 0,'1': 0, '1,5': 0,'2': 0,'2,5': 0,'3': 0,'3,5': 0,'4': 0,'4,5': 0,'5': 0 }
        for review in product["reviews"]:
            if review['recommendation'] == 'Polecam':
                recs['Polecam'] += 1
            else:
                recs['Nie Polecam'] += 1
            rating[review['productRate'].split("/")[0]] += 1
        
        return render_template("productCharts.html", pieData=recs, lineData=rating)

if __name__ == '__main__':
    app.run(debug=True)