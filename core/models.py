from django.db import models
from django.contrib.auth.models import User

# 
# Schema
# -----------------
# Image(pk, caption, owner, created, updated)
# Ranking(pk, userID, imageID, categoryID, ranking)
# Category(pk, title)
#

class Category(models.Model):
    """
    Every image is rated within a category.
    """
    title = models.TextField()

class Image(models.Model):
    """
    Object for each image in the system.
    """
    caption = models.TextField()
    user = models.ForeignKey(User, blank=True, null=True)
    url = models.URLField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category)
    
    def apply_categories(self, categories):
        """
        Apply a list of initially selected categories
        to this image by creating a ranking for each
        category listing.
        @param categories List of primary keys of categories
        """
        for cat_pk in categories:
            category = Category.objects.get(pk=cat_pk)
            self.categories.add(category)
    
    @staticmethod
    def create_image(url, caption):
        """
        Create an image from a url if that image is not already
        found in the database.
        """
        im = Image(url=url, caption=caption)
        im.save()
        
class VoteCount(models.Model):
    image = models.PositiveIntegerField()
    category = models.PositiveIntegerField()
    votes = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class Vote(models.Model):
    user        =   models.ForeignKey(User)
    votecount   =   models.ForeignKey(VoteCount)
    score       =   models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def update_vote_count(self, score_change):
        self.votecount.votes += score_change
        self.votecount.save()
        return self.votecount.votes

    def undo(self, new_score):
        ## If the new score == old score, this is an 'undo'
        should_delete = self.score == new_score

        undo_change = self.score * -1 # This undoes the vote
        votes = self.update_vote_count(undo_change)
        if should_delete:
            self.delete()
        return should_delete, votes

    @staticmethod
    def submit_vote(request):
        new_score = int(request.POST['action'])

        created = False
        try:
            votecount = VoteCount.objects.get(
                            image = request.POST['image'],
                            category = request.POST['cat']
                        )
        except VoteCount.DoesNotExist:
            votecount = VoteCount(
                            image = request.POST['image'],
                            category = request.POST['cat'],
                            votes = 0
                        )
            votecount.save()
        
        try:
            vote = Vote.objects.get(
                            user=request.user, 
                            votecount=votecount
                        )
            should_delete, votes = vote.undo(new_score=new_score)
            if should_delete:
                return votes
        except Vote.DoesNotExist:
            vote = Vote(
                            user=request.user,
                            votecount=votecount
                        )
            created = True
        vote.score = new_score
        vote.save()      
        return vote.update_vote_count(new_score)

    def __unicode__(self):
        return "%s voted on %c %d %d" % (self.user.name(), self.kind, self.id, self.score)


    
