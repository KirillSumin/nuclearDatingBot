from django.contrib import admin
from django.urls import include, path

from tgbot.views import login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login, name='login'),
    path('', include('tgbot.urls'))
]
