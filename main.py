from flask import (
    Flask,
    render_template
)
import requests
import logging
import Review as Review
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route('/', methods=["GET"])
def index():
    global requestedUrl
    page = 1
    hasNextPage = True
    totalReviews = 0
    while(hasNextPage):
        # app.logger.info(page)
        requestedUrl = f'https://www.ceneo.pl/94823130/opinie-{page}'
        requestedPage = requests.get(requestedUrl)
        soup = BeautifulSoup(requestedPage.content, "html.parser")
        allCommentsSection = soup.find(class_="js_product-reviews js_reviews-hook js_product-reviews-container")
        comments = allCommentsSection.find_all("div", class_="user-post user-post__card js_product-review")
        for comment in comments:
            review = scrapReview(comment)
            app.logger.info(review.getLogData())
        if len(comments) < 10:
            hasNextPage = False
        totalReviews += len(comments)
        page += 1
        # app.logger.info(totalReviews)
    return "results"

def scrapReview(comment):
    reviewId = comment.get('data-entry-id')
    authorName = comment.find("span", class_="user-post__author-name").text
    productRate = comment.find("span", class_="user-post__score-count").text
    commentContent = comment.find("div", class_="user-post__text").text
    recommendation = comment.find("span", class_="user-post__author-recomendation").text
    confirmedPurchase = "Opinia nie potwierdzona zakupem"
    if comment.find("div", class_="review-pz"):
        confirmedPurchase = comment.find("div", class_="review-pz").text
    dates = comment.find("span", class_="user-post__published").find_all("time")
    publishedDate = dates[0].get("datetime")
    purchasedDate = ""
    if len(dates) > 1:
        purchasedDate = dates[1].get("datetime")
    return Review.ReviewComment(reviewId, authorName, productRate, commentContent, recommendation, confirmedPurchase, publishedDate, purchasedDate)

if __name__ == '__main__':
    app.run(debug=True)