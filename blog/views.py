from django.shortcuts import render,redirect
from .models import Post,Category,Tag
from django.views.generic import ListView,DetailView,CreateView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
# Create your views here.

class PostUpdate(UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    template_name = 'blog/post_update_form.html'
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate,self).form_valid(form)
        self.object.tag.clear()
        tag_str = self.request.POST.get('tag_str')
        if tag_str:
            tag_str = tag_str.strip()
            tag_str = tag_str.replace(',', ';')
            tag_list = tag_str.split(';')
            for t in tag_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tag.add(tag)
        return response

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostUpdate, self).get_context_data() ##템플릿에서 필요한 거 담아서 전달
        if self.object.tag.exists():
            tag_str_list = list()
            for t in self.object.tag.all():
                tag_str_list.append(t.name)
            context['tag_str_default'] = ';'.join(tag_str_list)
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count
        return context
class PostCreate(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model = Post
    fields = ['title','hook_text','content','head_image','file_upload','category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff):
            form.instance.author = current_user
            response = super(PostCreate,self).form_valid(form)
            tag_str = self.request.POST.get('tag_str')
            if tag_str:
                tag_str = tag_str.strip()
                tag_str = tag_str.replace(',',';')
                tag_list = tag_str.split(';')
                for t in tag_list:
                    t = t.strip()
                    tag, is_tag_created =Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t,allow_unicode = True)
                        tag.save()
                    self.object.tag.add(tag)
            return response
        else:
            return redirect('/blog/')


    #템플릿 : 모델명_form.html
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostCreate, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count
        return context

class PostList(ListView):
    model = Post
    ordering = '-pk'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList,self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count
        return context
    # 템플릿 모델명_list.html : post_list.html
    # 파라미터 모델명_list : post_list

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail,self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count
        return context

def category_page(request,slug):

    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list =  Post.objects.filter(category=category)
    return render(
        request, 'blog/post_list.html',{
            'category' : category,
            'post_list' : post_list,
            'categories' : Category.objects.all(),
            'no_category_post_count' : Post.objects.filter(category=None).count
        }
    )
    # 템플릿 모델명_detail.html : post_detail.html
    # 파라미터 모델명 : post

def tag_page(request,slug):
    tag =Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request, 'blog/post_list.html',{
            'tag': tag,
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count
        }

    )

#def index(request):
#    posts1 = Post.objects.all().order_by('-pk')
#    return render(request,'blog/index.html',{'posts':posts1})

#def single_post_page(request, pk):
#    post = Post.objects.get(pk=pk)
#    return render(request, 'blog/single_post_page.html',{'post':post})

