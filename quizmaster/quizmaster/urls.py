"""quizmaster URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]


urlpatterns += (
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='admin/login.html'),name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', RedirectView.as_view(url='/main/', permanent=True)),
    path('main/',  views.main, name='main'),
    path('home/',  views.home, name='home'),
    path('gamer/list/',  views.gamer_list, name='gamer_list'),
    path('tools/', views.tools, name='tools'),
    path('help/', views.quiz_help, name='quiz_help'),

    path('quiz/',  views.quiz, name='quiz'),
    path('quiz/result/',  views.quiz_result, name='quiz_result'),
    path('quiz/import/',  views.quiz_import, name='quiz_import'),
    path('quiz/export/',  views.quiz_export, name='quiz_export'),
    path('quiz/session/delete/<int:sid>',  views.quiz_session_delete, name='quiz_session_delete'),
    path('quiz/print/result/<int:sid>',  views.quiz_result_to_pdf, name='quiz_print_result'),
    path("quiz/export/result/<int:sid>/<str:export>",  views.quiz_result_export, name='quiz_result_export'),
    path("quiz/export/queries/<int:qid>/<str:export>",  views.quiz_queries_export, name='quiz_queries_export'),
    path("quiz/mqtt/options/",  views.quiz_mqtt_options, name='quiz_mqtt_options'),

    path("box/mqtt/options/",  views.box_mqtt_options, name='box_mqtt_options'),
    path('box/', views.box, name='box'),
    path('box/login/', views.login_to_box, name='login_to_box'),

)

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

