from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from studysite.models import Studysite, Tag
from studysite.forms import SnippetForm, AnswerForm
from django.contrib.auth.models import User


# Create your views here.
def top(request):
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
    return render(request, 'snippets/top.html', context)


@login_required  # このデコレータのある機能はログインが必要
def snippet_new(request):
    if request.method == 'POST':
        form = SnippetForm(request.POST, request.FILES)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.created_by = request.user
            snippet.save()
            return redirect(snippet_detail, snippet_id=snippet.pk)
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
    snippet = get_object_or_404(Studysite, pk=snippet_id)
    return render(request, 'snippets/snippet_detail.html', {'snippet': snippet})

def profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    snippets = Studysite.objects.filter(created_by=user)

    context = {
        'user_profile': user,
        'snippets': snippets
    }
    return render(request, 'profile.html', context)

@login_required
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