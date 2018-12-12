from django.conf.urls import include, url
from .views import YoMamaBotView

urlpatterns = [
                  url(r'^55e9e04cd1a0eadaf6dc0793b17eeef318b5498d7fd1d5f367/?$', YoMamaBotView.as_view())
               ]