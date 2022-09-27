from django.urls import path
from . import  views

urlpatterns = [ #IP주소/blog
    path('',views.index),
    path('<int:pk>', views.single_post_page)
]