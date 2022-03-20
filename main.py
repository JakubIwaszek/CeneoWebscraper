from flask import (
    Flask,
    render_template,
    request
)
import requests
import logging
import Review as Review
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
    ## Wywal to do innej funkcji
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
            # app.logger.info(review.getLogData())
        if len(comments) < 10:
            hasNextPage = False
        totalReviews += len(comments)
        page += 1
        # app.logger.info(totalReviews)
    return render_template("homepage.html")

@app.route('/extract', methods=["POST", "GET"])
def extractOpinions():
    app.logger.info(request.form['productId'])
    return render_template("extractOpinion.html")

## move to another file
def getReviews(pageId):
    app.logger.info(pageId)

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
    # app.logger.info(advantages)
    return Review.ReviewComment(reviewId, authorName, productRate, commentContent, recommendation, confirmedPurchase, publishedDate, purchaseDate, likesCount, dislikesCount, advantages, len(advantages), disAdvantages, len(disAdvantages))

if __name__ == '__main__':
    app.run(debug=True)