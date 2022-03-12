class ReviewComment():
    def __init__(self, id, authorName, productRate, commentText, recommendation, confirmedPurchase, publishedDate, purchaseDate):
        self.id = id
        self.authorName = authorName
        self.productRate = productRate
        self.commentText = commentText
        self.recommendation = recommendation
        self.confirmedPurchase = confirmedPurchase
        self.publishedDate = publishedDate
        self.purchaseDate = purchaseDate

    def getLogData(self):
        return "\n Review id: " + self.id + "\n Author name: " + self.authorName + " \n Product rate: " + self.productRate + "\n Comment: " + self.commentText + "\n Recommendation: " + self.recommendation + "\n Confirmed purchase: " + self.confirmedPurchase + "\n Published date: " + self.publishedDate + " - Purchase date: " + self.purchaseDate