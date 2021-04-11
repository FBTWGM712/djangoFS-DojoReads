from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('registration', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('books', views.books),
    path('books/<int:id>', views.view_book),
    path('books/confirm_delete_review/<int:id>', views.confirm_delete_review),
    path('books/delete_review/<int:id>', views.delete_review),
    path('books/add', views.add),
    path('books/add_book_to_db', views.add_book_to_db),
    path('books/<int:book_id>/add_review', views.add_review),
    path('users/<int:id>', views.user),
]