from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm


class Article(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    body = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='static/images/', null=True, default='static/images/user-1.jpg')


class Comment(models.Model):
    title = models.CharField(max_length=180)
    body = models.CharField(max_length=700, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="comment", on_delete=models.CASCADE)
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE, null=True)


class Reply(models.Model):
    title = models.CharField(max_length=180)
    body = models.CharField(max_length=700, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="reply", on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name="replies", on_delete=models.CASCADE, null=True)


class AddCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('title', 'body')


class AddReplyForm(ModelForm):
    class Meta:
        model = Reply
        fields = ('title', 'body')
