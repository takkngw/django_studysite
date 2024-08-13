import qrcode
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from studysite.models import Studysite, Tag, Comment
from studysite.forms import SnippetForm, AnswerForm, CommentForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from io import BytesIO


# Create your views here.
def top(request):
    subject_name = request.GET.get('subject')  # クエリパラメータ 'subject' を取得
    snippet_level = request.GET.get('level')  # クエリパラメータ 'level' を取得
    if subject_name:
        snippets = Studysite.objects.filter(tags__name=subject_name)  # タグ名でフィルタリング
    elif snippet_level:
        snippets = Studysite.objects.filter(level=snippet_level)
    else:
        snippets = Studysite.objects.all()

    tags = Tag.objects.all()
    return render(request, 'snippets/top.html', {'snippets': snippets, 'tags': tags})


@login_required  # このデコレータのある機能はログインが必要
def snippet_new(request):
    if request.method == 'POST':
        form = SnippetForm(request.POST, request.FILES)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.created_by = request.user
            form.save()
            return redirect('snippet_detail', snippet_id=snippet.pk)
    else:
        form = SnippetForm()
    return render(request, 'snippets/snippet_new.html', {'form': form})


@login_required  # このデコレータのある機能はログインが必要
def snippet_edit(request, snippet_id):
    snippet = get_object_or_404(Studysite, pk=snippet_id)
    if snippet.created_by_id != request.user.id:
        return HttpResponseForbidden('このスニペットの編集は許可されていません．')
    if request.method == 'POST':
        form = SnippetForm(request.POST, request.FILES, instance=snippet)
        if form.is_valid():
            form.save()
            return redirect('snippet_detail', snippet_id=snippet_id)
    else:
        form = SnippetForm(instance=snippet)
    return render(request, 'snippets/snippet_edit.html', {'form': form})


def snippet_detail(request, snippet_id):
    snippet = get_object_or_404(Studysite, id=snippet_id)
    liked_snippets = request.COOKIES.get('liked_snippets', '').split(',')
    liked = str(snippet_id) in liked_snippets
    comments = snippet.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.snippet = snippet
            comment.save()
            return redirect('snippet_detail', snippet_id=snippet_id)
    else:
        form = CommentForm()

    context = {
        'snippet': snippet,
        'liked': liked,
        'comments': comments,
        'form': form,
    }
    return render(request, 'snippets/snippet_detail.html', context)

@login_required
def bookmark_post(request, post_id):
    post = get_object_or_404(Studysite, id=post_id)
    
    if request.user in post.bookmarks.all():
        post.bookmarks.remove(request.user)
        is_bookmarked = False
    else:
        post.bookmarks.add(request.user)
        is_bookmarked = True

    return JsonResponse({'is_bookmarked': is_bookmarked})


def profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    snippets = Studysite.objects.filter(created_by=user)

    context = {
        'user_profile': user,
        'snippets': snippets
    }
    return render(request, 'profile.html', context)


def snippet_answer(request, snippet_id):
    snippet = get_object_or_404(Studysite, pk=snippet_id)
    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=snippet)
        if form.is_valid():
            form.save()
            return redirect('snippet_detail', snippet_id=snippet_id)
    else:
        form = AnswerForm(instance=snippet)
    return render(request, 'snippets/snippet_answer.html', {'snippet': snippet, 'form': form})


def unanswered(request):
    tags = Tag.objects.all()
    raw_query = request.META.get('QUERY_STRING', '')  # URLのクエリストリング全体を取得
    query_param = raw_query.strip('?')  # '?'を取り除いて値を取得
    snippets = Studysite.objects.all() # Snippetの一覧を取得
    selected_tag = request.GET.get('tag')
    
    try:
        query_param = int(query_param)
        # selected_tag = get_object_or_404(Tag, id=query_param)
        snippets = Studysite.objects.filter(tags=query_param)
    except (ValueError, Tag.DoesNotExist):
        snippets = Studysite.objects.all()
    
    context = {'snippets': snippets, 'tags': tags, 'selected_tag': selected_tag, 'query_param': query_param}
    if selected_tag:
        snippets = snippets.filter(tags__id=selected_tag)
    return render(request, 'snippets/unanswered.html', {'snippets': snippets})


def like_snippet(request, snippet_id):
    snippet = get_object_or_404(Studysite, pk=snippet_id)
    
    # クッキーでいいねの状態をチェック
    liked_snippets = request.COOKIES.get('liked_snippets', '').split(',')
    
    if str(snippet_id) in liked_snippets:
         # いいねを取り消す場合
        liked_snippets.remove(str(snippet_id))
        snippet.likes -= 1
        snippet.save()
        
        response = JsonResponse({'likes': snippet.likes, 'liked': False})
        response.set_cookie('liked_snippets', ','.join(liked_snippets))
        return response
    else:
        snippet.likes += 1
        snippet.save()
        
        liked_snippets.append(str(snippet_id))
        response = JsonResponse({'likes': snippet.likes, 'liked': True})
        response.set_cookie('liked_snippets', ','.join(liked_snippets))
        return response
    
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Studysite, id=post_id)

    if request.method == "POST":
        if request.user == post.created_by:
            post.delete()
            messages.success(request, "投稿が削除されました。")
            return redirect('top')  # 削除後にリダイレクトするページを設定
        else:
            messages.error(request, "この投稿を削除する権限がありません。")
            return redirect('snippet_detail', post_id=post_id)
    else:
        return redirect('snippet_detail', post_id=post_id)

def generate_qr_code(request):
    # 現在のフルURLを取得
    current_url = request.build_absolute_uri()

    # QRコードの生成
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(current_url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # 画像をバイトストリームに変換
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')