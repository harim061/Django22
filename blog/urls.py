from django.urls import path
from . import  views

urlpatterns = [ #IP주소/blog
    path('',views.PostList.as_view()),
    path('<int:pk>/',views.PostDetail.as_view())

    #path('',views.index),
    #path('<int:pk>/', views.single_post_page)
]