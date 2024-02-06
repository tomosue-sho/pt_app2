from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import DeleteView
from django.views import generic
from django.urls import reverse_lazy
from django.utils import timezone
from pt_kokushi.models.post_models import Post, Comment
from pt_kokushi.forms.post_forms import PostForm
from pt_kokushi.forms.post_forms import CommentForm

#掲示板用
class PostListView(generic.ListView):
    model = Post
    template_name = 'posts/post_list.html'
    paginate_by = 12  # 1ページあたりのアイテム数
    page_kwarg = 'p'  # クエリパラメータ 'p' をページネーションのために使用
    context_object_name = 'posts'
    ordering = ['-last_commented_at']

class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context

class PostCreateView(generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_create.html'

    def form_valid(self, form):
        return super().form_valid(form)
    
    success_url = reverse_lazy('pt_kokushi:post_list')

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            if not comment.nickname:
                comment.nickname = "Anonymous"
            comment.author = request.user
            comment.save()
            
            # 最新のコメント日時を更新
            post.last_commented_at = timezone.now()
            post.save(update_fields=['last_commented_at'])

            return redirect('pt_kokushi:post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'posts/add_comment_to_post.html',  {'form': form, 'post': post})

class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('pt_kokushi:post_list')
    
    def test_func(self):
        return self.request.user.is_staff

class CommentDeleteView(UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'posts/comment_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('pt_kokushi:post_detail', kwargs={'pk': self.object.post.pk})
    
    def test_func(self):
        return self.request.user.is_staff