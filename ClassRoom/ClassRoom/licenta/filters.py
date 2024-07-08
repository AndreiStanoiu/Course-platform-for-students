import django_filters
from .models import Book
from django_filters import CharFilter

class MyModelFilter(django_filters.FilterSet):
    title = CharFilter(field_name='name',lookup_expr='icontains',label='Title')
    author = CharFilter(field_name='author',lookup_expr='icontains',label='Author')
    class Meta:
        model = Book
        # Declare all your model fields by which you will filter
        # your queryset here:
        fields = ['name']
        exclude = ['name']