from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from .models import Article, Reply, AddReplyForm, AddCommentForm, Comment
from django.urls import reverse


class NewsView(ListView):
    model = Article
    template_name = 'news.html'
    context_object_name = 'articles'
    ordering = ['-publication_date']
    paginate_by = 10
    queryset = Article.objects.all()


class ArticleInfoView(View):
    def get(self, request, pk):
        article = Article.objects.get(pk=pk)
        return render(request, 'article.html', {'article': article})


class AddCommentView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        form = AddCommentForm()

        return render(request, 'add_comment.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request, pk):
        if request.method == 'POST':
            form = AddCommentForm(request.POST)
            article = Article.objects.get(pk=pk)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.created_by = request.user
                comment.save()
                article.comments.add(comment)
                article.save()
                comment.save()
                form.save_m2m()
            return HttpResponseRedirect(reverse('articleinfo', args=[pk]))


class AddReplyView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        form = AddReplyForm()

        return render(request, 'add_reply.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request, pk):
        if request.method == 'POST':
            form = AddReplyForm(request.POST)
            comment = Comment.objects.get(pk=pk)
            if form.is_valid():
                reply = form.save(commit=False)
                reply.created_by = request.user
                reply.save()
                comment.replies.add(reply)
                comment.save()
                reply.save()
                form.save_m2m()
            return HttpResponseRedirect(reverse('articleinfo', args=[comment.article.pk]))

# Create your views here.
