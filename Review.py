class ReviewComment():
    def __init__(self, id, authorName, productRate, commentText, recommendation):
        self.id = id
        self.authorName = authorName
        self.productRate = productRate
        self.commentText = commentText
        self.recommendation = recommendation

    def getLogData(self):
        return "\n Review id: " + self.id + "\n Author name: " + self.authorName + " \n Product rate: " + self.productRate + "\n Comment: " + self.commentText + "\n Recommendation: " + self.recommendation