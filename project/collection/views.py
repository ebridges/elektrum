from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from django.http import HttpResponseForbidden

from collection.models import Collection

class CollectionForm(ModelForm):
    class Meta:
        model = Collection
        fields = ['path']

def collection_list(request, template_name='collection/collection_list.html'):
    collection = Collection.objects.all()
    data = {}
    data['object_list'] = collection
    return render(request, template_name, data)


def collection_view(request, pk, template_name='collection/collection_detail.html'):
    collection = get_object_or_404(Collection, pk=pk)    
    return render(request, template_name, {'object':collection})


def collection_create(request, template_name='collection/collection_form.html'):
    form = CollectionForm(request.POST or None)
    return _save_collection_form(request, form)


def collection_edit(request, pk, template_name='collection/collection_form.html'):
    collection= get_object_or_404(Collection, pk=pk)
    form = CollectionForm(request.POST or None, instance=collection)
    return _save_collection_form(request, form)


def collection_delete(request, pk, template_name='collection/collection_confirm_delete.html'):
    collection= get_object_or_404(Collection, pk=pk)    
    if request.method=='POST':
        collection.delete()
        return redirect('collection_list')
    return render(request, template_name, {'object':collection})


def _save_collection_form(request, form, template_name='collection/collection_form.html'):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if form.is_valid():
        form.instance.user = request.user
        form.save()
        return redirect('collection_list')
    return render(request, template_name, {'form':form})
