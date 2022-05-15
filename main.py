from flask import (
    Flask,
    flash,
    render_template,
    redirect,
    request
)
import requests
import logging
import json
import os
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
    return render_template("productsList.html")

def saveProductAsJson(product):
    with open(os.path.join('products', f"{product.id}.json"), "w") as file:
        file.write(product.toJSON())

def getProductData(productId):
    requestedUrl = f'https://www.ceneo.pl/{productId}'
    requestedPage = requests.get(requestedUrl)
    soup = BeautifulSoup(requestedPage.content, "html.parser")
    productTitle = soup.find(class_="product-top__product-info__name").text.strip()
    averageRating = soup.find(class_="product-review__score").text.strip()
    numberOfReviews = soup.find(class_="product-review__link").find("span").text.strip()
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
        comments = allCommentsSection.find_all("div", class_="user-post user-post__card js_product-review")
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
    recommendation = comment.find("span", class_="user-post__author-recomendation").text.strip()
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