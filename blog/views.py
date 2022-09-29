from django.shortcuts import render
from .models import Post
from django.views.generic import ListView,DetailView
# Create your views here.

class PostList(ListView):
    model = Post
    ordering = '-pk'
    # 템플릿 모델명_list.html : post_list.html
    # 파라미터 모델명_list : post_list

class PostDetail(DetailView):
    model = Post
    # 템플릿 모델명_detail.html : post_detail.html
    # 파라미터 모델명 : post

#def index(request):
#    posts1 = Post.objects.all().order_by('-pk')
#    return render(request,'blog/index.html',{'posts':posts1})

#def single_post_page(request, pk):
#    post = Post.objects.get(pk=pk)
#    return render(request, 'blog/single_post_page.html',{'post':post})

