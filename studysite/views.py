from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from studysite.models import Studysite, Comment, VisitorCounter, TagGroup
from studysite.forms import SnippetForm, AnswerForm, CommentForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.
def top(request):
    school_name = request.GET.get('school')
    subjects_name = request.GET.get('subjects')
    subject_name = request.GET.get('subject')
    field_name = request.GET.get('field')
    # フィルタ条件を動的に組み立てる
    filters = {}
    if school_name:
        filters['tag_groups__parent__parent__parent__name'] = school_name
    if subjects_name:
        filters['tag_groups__parent__parent__name'] = subjects_name
    if subject_name:
        filters['tag_groups__parent__name'] = subject_name
    if field_name:
        filters['tag_groups__name'] = field_name

    # フィルタリング
    if filters:
        snippets = Studysite.objects.filter(**filters).distinct()
    else:
        snippets = Studysite.objects.all()
        
    counter, created = VisitorCounter.objects.get_or_create(id=1)
    
    # カウンターをインクリメント
    counter.count += 1
    counter.save()
    tag_groups = TagGroup.objects.filter(parent__isnull=True).order_by('order').prefetch_related('children__children')
    return render(request, 'snippets/top.html', {'snippets': snippets, 'visitor_number': counter.count, 'tag_groups': tag_groups})


@login_required  # このデコレータのある機能はログインが必要
def snippet_new(request):
    if request.method == 'POST':
        form = SnippetForm(request.POST, request.FILES)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.created_by = request.user
            selecttags = request.POST.getlist('tag_groups')
            snippet.save()
            return redirect('snippet_detail', snippet_id=snippet.pk)
        else:
            print(form.errors)
    else:
        form = SnippetForm()
    tag_groups = TagGroup.objects.filter(parent__isnull=True).order_by('order').prefetch_related('children__children')
    return render(request, 'snippets/snippet_new.html', {'form': form, 'tag_groups': tag_groups})



@login_required  # このデコレータのある機能はログインが必要
def snippet_edit(request, snippet_id):
    snippet = get_object_or_404(Studysite, pk=snippet_id)
    tag_groups = TagGroup.objects.filter(parent__isnull=True).order_by('order').prefetch_related('children__children')
    if snippet.created_by_id != request.user.id:
        return HttpResponseForbidden('このスニペットの編集は許可されていません．')
    if request.method == 'POST':
        form = SnippetForm(request.POST, request.FILES, instance=snippet)
        if form.is_valid():
            form.save()
            return redirect('snippet_detail', snippet_id=snippet_id)
    else:
        form = SnippetForm(instance=snippet)
    return render(request, 'snippets/snippet_edit.html', {'form': form, 'tag_groups': tag_groups})


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
        
    tag_groups = TagGroup.objects.filter(parent__isnull=True).order_by('order').prefetch_related('children__children')

    context = {
        'snippet': snippet,
        'liked': liked,
        'comments': comments,
        'form': form,
        'tag_groups': tag_groups
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
    tag_groups = TagGroup.objects.filter(parent__isnull=True).order_by('order').prefetch_related('children__children')

    context = {
        'user_profile': user,
        'snippets': snippets,
        'tag_groups': tag_groups
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
        
    tag_groups = TagGroup.objects.filter(parent__isnull=True).order_by('order').prefetch_related('children__children')
    return render(request, 'snippets/snippet_answer.html', {'snippet': snippet, 'form': form, 'tag_groups': tag_groups})


def unanswered(request):
    tag_groups = TagGroup.objects.filter(parent__isnull=True).order_by('order').prefetch_related('children__children')
    raw_query = request.META.get('QUERY_STRING', '')  # URLのクエリストリング全体を取得
    query_param = raw_query.strip('?')  # '?'を取り除いて値を取得
    snippets = Studysite.objects.all() # Snippetの一覧を取得
    selected_tag = request.GET.get('tag')
    
    try:
        query_param = int(query_param)
        # selected_tag = get_object_or_404(Tag, id=query_param)
        snippets = Studysite.objects.filter(tags=query_param)
    except (ValueError, TagGroup.DoesNotExist):
        snippets = Studysite.objects.all()
    
    context = {'snippets': snippets, 'tag_groups': tag_groups, 'selected_tag': selected_tag, 'query_param': query_param}
    if selected_tag:
        snippets = snippets.filter(tags__id=selected_tag)
    return render(request, 'snippets/unanswered.html', context)


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
