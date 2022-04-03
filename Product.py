import json

class ProductDetails():
    def __init__(self, id, title, allReviewsCount, allAdvantagesCount, allDisadvantagesCount, averageRating):
        self.id = id
        self.title = title
        self.allReviewsCount = allReviewsCount
        self.allAdvantagesCount = allAdvantagesCount
        self.allDisadvangatesCount = allDisadvantagesCount
        self.averageRating = averageRating
