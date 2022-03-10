from flask import (
    Flask,
    render_template
)
import requests
import logging
from bs4 import BeautifulSoup

app = Flask(__name__)
@app.route('/', methods=["GET"])

def index():
    global requestedUrl, tag
    #TODO: Implement mechanism to get only opinions, not the whole site
    requestedUrl = 'https://www.ceneo.pl/94823130/opinie-1'
    tag = 'div'
    requestedPage = requests.get(requestedUrl)
    soup = BeautifulSoup(requestedPage.content, "html.parser")
    allCommentsSection = soup.find(class_="js_product-reviews js_reviews-hook js_product-reviews-container")
    comments = allCommentsSection.find_all("div", class_="user-post user-post__card js_product-review")
    for comment in comments:
        authorName = comment.find("span", class_="user-post__author-name").text
        productRate = comment.find("span", class_="user-post__score-count").text
        commentContent = comment.find("div", class_="user-post__text").text
        app.logger.info(authorName + "  ^  " + productRate + "  ^  " + commentContent)
    return "results"

if __name__ == '__main__':
    app.run(debug=True)