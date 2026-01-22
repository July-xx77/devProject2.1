from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import  get_object_or_404
from .models import Post
from django.shortcuts import redirect
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from .serializers import PostSerializer
from rest_framework import generics
from django.contrib.auth import logout

def custom_logout(request):
    logout(request)
    return redirect('timeline')

def timeline(request):
    posts = Post.objects.all().order_by('-created_at')
    context = {
        'posts': posts,
}
    return render(request, 'timeline.html', context)


def post_detail(request, pk):
    # pkを使って、Postオブジェクトを1件だけ取得する
    # 存在しない場合は404エラーを返す
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'post_detail.html', {'post': post})

@login_required
def post_create(request):
    # 1. POSTリクエスト（送信ボタン押下時）の処理
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('timeline')
        # (POSTで無効だった場合は、下の 'return render' に進む)

    # 2. GETリクエスト（ページ初回表示時）の処理
    else:
        form = PostForm() # 空のフォームを作成
    # 3. GETリクエスト、または POSTが失敗した場合
    return render(request, 'post_create.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk) # 権限チェック：投稿者とログインユーザーが一致しない場合はリダイレクト
    if request.user != post.author:
        return redirect('post_detail', pk=pk)
    if request.method == 'POST':
        # 既存のインスタンスを渡してフォームを生成
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=pk)
    else:
        # 既存のインスタンスを渡してフォームを生成（初期表示）
        form = PostForm(instance=post)
    return render(request, 'post_edit.html', {'form': form, 'post': post})
    
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('post_detail', pk=pk)
    if request.method == 'POST':
        post.delete() # データを削除
        return redirect('timeline') # タイムラインにリダイレクト
    return render(request, 'post_confirm_delete.html', {'post': post})

def timeline(request): # URLのクエリパラメータから'q'の値を取得する
    query = request.GET.get('q')
    if query:
    # もしクエリがあれば、contentにその文字列を含む投稿をフィルタリング
        posts = Post.objects.filter(content__icontains=query).order_by('-created_at')
    else:
    # クエリがなければ、全ての投稿を表示
        posts = Post.objects.all().order_by('-created_at')
    context = {
        'posts': posts,
        'query': query, # 検索キーワードをテンプレートに渡す
        }
    return render(request, 'timeline.html', context)

class PostListAPIView(generics.ListAPIView):
# どのデータの一覧を返すか
    queryset = Post.objects.all()
    # どの翻訳者（シリアライザ）を使ってJSONに変換するか
    serializer_class = PostSerializer

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login') # 登録成功後はログインページへ
    template_name = 'signup.html'


