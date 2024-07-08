from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from studysite.models import Studysite
from studysite.forms import SnippetForm
from django.contrib.auth.models import User


# Create your views here.
def top(request):
    snippets = Studysite.objects.all() # Snippetの一覧を取得
    context = {'snippets': snippets}
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

