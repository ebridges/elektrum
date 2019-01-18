from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from collection.models import Collection

class CollectionList(ListView):
    model = Collection

class CollectionView(DetailView):
    model = Collection

class CollectionCreate(CreateView):
    model = Collection
    fields = ['path']
    success_url = reverse_lazy('collection_list')

class CollectionUpdate(UpdateView):
    model = Collection
    fields = ['path']
    success_url = reverse_lazy('collection_list')

class CollectionDelete(DeleteView):
    model = Collection
    success_url = reverse_lazy('collection_list')
