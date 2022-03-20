class ReviewComment():
    def __init__(self, id, authorName, productRate, commentText, recommendation, confirmedPurchase, publishedDate, purchaseDate, likesCount, dislikesCount, advantages, advantagesCount, disAdvantages, disAdvantagesCount):
        self.id = id
        self.authorName = authorName
        self.productRate = productRate
        self.commentText = commentText
        self.recommendation = recommendation
        self.confirmedPurchase = confirmedPurchase
        self.publishedDate = publishedDate
        self.purchaseDate = purchaseDate
        self.likesCount = likesCount
        self.dislikesCount = dislikesCount
        self.advantages = advantages
        self.advantagesCount = advantagesCount
        self.disAdvantages = disAdvantages
        self.disAdvantagesCount = disAdvantagesCount

    def getLogData(self):
        return "\n Review id: " + self.id + "\n Author name: " + self.authorName + " \n Product rate: " + self.productRate + "\n Comment: " + self.commentText + "\n Recommendation: " + self.recommendation + "\n Confirmed purchase: " + self.confirmedPurchase + "\n Published date: " + self.publishedDate + " - Purchase date: " + self.purchaseDate + "\n Likes count: " + self.likesCount + "\n Dislikes count: " + self.dislikesCount + "\n Advantages: " + str(self.advantagesCount) + "\n List: " + " ".join(self.advantages) + "\n Disadvantages: " + str(self.disAdvantagesCount) + "\n List: " + " ".join(self.disAdvantages)