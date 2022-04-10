import json

class ProductDetails():
    def __init__(self, id, title, allReviewsCount, allAdvantagesCount, allDisadvantagesCount, averageRating, reviews):
        self.id = id
        self.title = title
        self.allReviewsCount = allReviewsCount
        self.allAdvantagesCount = allAdvantagesCount
        self.allDisadvangatesCount = allDisadvantagesCount
        self.averageRating = averageRating
        self.reviews = reviews

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)