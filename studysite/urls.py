from django.urls import path
from studysite import views 
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from .views import like_snippet



urlpatterns = [
    path('', views.top, name='top'),
    path('new/', views.snippet_new, name = 'snippet_new'),
    path('snippet/<int:snippet_id>/', views.snippet_detail, name = 'snippet_detail'),
    path('snippet/<int:snippet_id>/edit/', views.snippet_edit, name = 'snippet_edit'),
    path('login/', LoginView.as_view(redirect_authenticated_user=True, 
                                     template_name='snippets/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', CreateView.as_view(template_name='snippets/signup.html', 
                                       form_class=UserCreationForm, success_url='/'), name='signup'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('snippet/<int:snippet_id>/answer/', views.snippet_answer, name='snippet_answer'),
    path('unanswered/', views.unanswered, name='unanswered'),
    path('like/<int:snippet_id>/', like_snippet, name='like_snippet'),
]
