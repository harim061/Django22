from django.shortcuts import render, redirect
from .models import Post, Category, Tag,Comment
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .froms import CommentForm
from django.shortcuts import get_object_or_404

# Create your views here.
class PostUpdate(UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category'] #,'tags'

    template_name = 'blog/post_update_form.html'
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()
        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')  # , -> ;로 바꿔준다
            tags_list = tags_str.split(';')  # ;를 기준으로 단어 나누기
            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)
        return response

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostUpdate, self).get_context_data() ##템플릿에서 필요한 거 담아서 전달
        if self.object.tags.exists():
            tags_str_list = list() #빈 리스트 생성
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = ';'.join(tags_str_list)
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count
        return context

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model=Post
    fields = ['title','hook_text','content','head_image','file_upload','category'] #, 'tags'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff):
            form.instance.author = current_user #form의 author값을 현재 로그인된 값으로 설정해줌
            response = super(PostCreate,self).form_valid(form)
            tags_str = self.request.POST.get('tags_str')
            if tags_str :
                tags_str = tags_str.strip()
                tags_str = tags_str.replace(',',';') #, -> ;로 바꿔준다
                tags_list = tags_str.split(';') #;를 기준으로 단어 나누기
                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return response
        else:
            return redirect('/blog/')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostCreate, self).get_context_data() ##템플릿에서 필요한 거 담아서 전달
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count
        return context

    # 템플릿 모델명_form.html : post_form.html (자동 생성>>템플릿 이름 명시 필요 없음)

class PostList(ListView):
    model = Post
    ordering = '-pk'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data() ##템플릿에서 필요한 거 담아서 전달
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count
        return context

    #템플릿 모델명_list.html : post_list.html (자동 생성>>템플릿 이름 명시 필요 없음)
    #파라미터 모델명_list : post_list
def new_comment(request,pk):
    if request.user.is_authenticated:
        post=get_object_or_404(Post,pk=pk)
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
            else:
                return redirect(post.get_absolute_url())
        else:
            raise PermissionDenied

class CommentUpdate(LoginRequiredMixin,UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail,self).get_context_data()
        context['categories']=Category.objects.all()
        context['no_category_post_count']=Post.objects.filter(category=None).count
        context['comment_form'] = CommentForm
        return context

    #템플릿 모델명_detail.html : post_detail.html (템플릿 이름을 자동으로 부름)
    #파라미터 모델명 : post

def category_page(request,slug):
    if slug=='no_category':
        category='미분류'
        post_list=Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug) #왼쪽 필드명, 오른쪽 url을 통해 전달된 slug값
        post_list=Post.objects.filter(category=category)
    return render(request, 'blog/post_list.html',
                  {'category' : category,
                   'post_list' : post_list, #Post.objects.filter(category=category)
                   'categories' : Category.objects.all(),
                   'no_category_post_count' : Post.objects.filter(category=None).count
                   })


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(request, 'blog/post_list.html', {
        'tag' : tag,
        'post_list' : post_list,
        'categories': Category.objects.all(),
        'no_category_post_count': Post.objects.filter(category=None).count

    })

#def index(request):
#    posts1 = Post.objects.all().order_by('-pk')
#    return render(request, 'blog/index.html', {'posts2': posts1}) #오른쪽 posts는 위에서 선언한 posts!


#def single_post_page(request, pk):
#    post2 = Post.objects.get(pk=pk) #왼쪽 pk는 post가 가지고 있는 field 이름
#    return render(request, 'blog/single_post_page.html', {'post': post2})