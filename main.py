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

def getProductsFromJsons():
    try:
        productsNames = os.listdir(os.getcwd() + '/products')
        products = []
        for productName in productsNames:
            app.logger.info(productName)
            app.logger.info(os.getcwd())
            with open(os.path.join('products', productName), "r") as file:
                data = json.load(file)
                products.append(data)
        return products
    except:
        return []

def saveProductAsJson(product):
    with open(os.path.join('products', f"{product.id}.json"), "w") as file:
        file.write(product.toJSON())

def getProductData(productId):
    requestedUrl = f'https://www.ceneo.pl/{productId}'
    requestedPage = requests.get(requestedUrl)
    soup = BeautifulSoup(requestedPage.content, "html.parser")
    productTitle = soup.find(class_="product-top__product-info__name").text.strip()
    averageRating = soup.find(class_="product-review__score").get("content")
    numberOfReviews = soup.find(class_="product-review__link").find("span").text.strip() if soup.find(class_="product-review__link").find("span") is not None else 0
    numberOfAdvantages = 0
    numberOfDisadvantages = 0
    reviews = getReviewsFromProduct(productId)
    for review in reviews:
        numberOfAdvantages += review.advantagesCount
        numberOfDisadvantages += review.disAdvantagesCount
    product = ProductDetails(productId, productTitle, numberOfReviews, numberOfAdvantages, numberOfDisadvantages, averageRating, reviews)
    return product

## move to another file
def getReviewsFromProduct(productId):
    requestedUrl = ""
    page = 1
    hasNextPage = True
    totalReviews = 0
    allReviews = []
    while(hasNextPage):
        requestedUrl = f'https://www.ceneo.pl/{productId}/opinie-{page}'
        requestedPage = requests.get(requestedUrl)
        soup = BeautifulSoup(requestedPage.content, "html.parser")
        allCommentsSection = soup.find(class_="js_product-reviews js_reviews-hook js_product-reviews-container")
        comments = allCommentsSection.find_all("div", class_="user-post user-post__card js_product-review") if allCommentsSection is not None else []
        for comment in comments:
            review = scrapReview(comment)
            allReviews.append(review)
        if len(comments) < 10:
            hasNextPage = False
        totalReviews += len(comments)
        page += 1
    return allReviews

### REVIEW Scrapper

def scrapReview(comment):
    reviewId = comment.get('data-entry-id')
    authorName = comment.find("span", class_="user-post__author-name").text.strip()
    productRate = comment.find("span", class_="user-post__score-count").text.strip()
    commentContent = comment.find("div", class_="user-post__text").text.strip()
    recommendation = comment.find("span", class_="user-post__author-recomendation").text.strip() if comment.find("span", class_="user-post__author-recomendation") is not None else "Brak"
    confirmedPurchase = "Opinia nie potwierdzona zakupem"
    if comment.find("div", class_="review-pz"):
        confirmedPurchase = comment.find("div", class_="review-pz").text.strip()
    dates = comment.find("span", class_="user-post__published").find_all("time")
    publishedDate = dates[0].get("datetime")
    purchaseDate = ""
    if len(dates) > 1:
        purchaseDate = dates[1].get("datetime")
    likesCount = comment.find("button", class_="vote-yes").get("data-total-vote")
    dislikesCount = comment.find("button", class_="vote-no").get("data-total-vote")
    advantages = []
    if comment.find("div", class_="review-feature__title--positives"):
        advantagesNodes = comment.find("div", class_="review-feature__title--positives").find_next_siblings("div", {"class": "review-feature__item"})
        for advantageSingleNode in advantagesNodes:
            advantage = advantageSingleNode.text.strip()
            advantages.append(advantage)
    disAdvantages = []
    if comment.find("div", class_="review-feature__title--negatives"):
        disAdvantagesNodes = comment.find("div", class_="review-feature__title--negatives").find_next_siblings("div", {"class": "review-feature__item"})
        for disAdvantageSingleNode in disAdvantagesNodes:
            disAdvantage = disAdvantageSingleNode.text.strip()
            disAdvantages.append(disAdvantage)
    return Review.ReviewComment(reviewId, authorName, productRate, commentContent, recommendation, confirmedPurchase, publishedDate, purchaseDate, likesCount, dislikesCount, advantages, len(advantages), disAdvantages, len(disAdvantages))

if __name__ == '__main__':
    app.run(debug=True)