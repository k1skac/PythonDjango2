from typing import Any
from django.http.request import HttpRequest as HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from followers.models import Follower
from .models import Post

class HomePage(TemplateView):
    http_method_names = ["get"]
    template_name = "feed/homepage.html"
    
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            following = list(Follower.objects.filter(followed_by=self.request.user).values_list('following', flat=True))
            if not following:
                posts = Post.objects.all().order_by('-id')[0:30] 
            else:  
                posts= Post.objects.filter(author__in=following).order_by('-id')[0:60]  
        else:
            posts = Post.objects.all().order_by('-id')[0:30]
        context['posts'] = posts 
        return context

## forcing to auth, can't create post without login
class PostDetailView(LoginRequiredMixin, DetailView):
    http_method_names= ["get"]
    template_name = 'feed/detail.html'
    model = Post
    context_object_name = 'post'

class CreateNewPost(CreateView):
    template_name = "feed/create.html"
    model = Post
    fields = ['title', 'text']
    success_url = "/"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()
        return super().form_valid(form)
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        post = Post.objects.create(
            text = request.POST.get("text"),
            title = request.POST.get("title"),
            author = request.user
        )
        return render(
            request,
            "includes/post.html",
            {
                "post": post,
                "show_detail_link": True
            },
           content_type="application/html" 
        )