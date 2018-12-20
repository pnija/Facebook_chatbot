from django.conf.urls import include, url
from .views import YoMamaBotView

urlpatterns = [
                  url(r'^a7983129cd9e543f5715077cff8b7a1e6f97450862fdb0a063/?$', YoMamaBotView.as_view())
               ]