from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from django.http import HttpResponseForbidden

from collection.models import Collection

class CollectionForm(ModelForm):
    class Meta:
        model = Collection
        fields = ['path']

def collection_list(request, template_name='collection/collection_list.html'):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(content='Authentication is required.')
    collection = Collection.objects.filter(user=request.user)
    data = {}
    data['object_list'] = collection
    return render(request, template_name, data)


def collection_view(request, pk, template_name='collection/collection_detail.html'):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(content='Authentication is required.')
    collection = get_object_or_404(Collection, pk=pk, user=request.user)    
    return render(request, template_name, {'object':collection})


def collection_create(request, template_name='collection/collection_form.html'):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(content='Authentication is required.')
    form = CollectionForm(request.POST or None)
    return _save_collection_form(request, form)


def collection_edit(request, pk, template_name='collection/collection_form.html'):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(content='Authentication is required.')
    collection= get_object_or_404(Collection, pk=pk, user=request.user)
    form = CollectionForm(request.POST or None, instance=collection)
    return _save_collection_form(request, form)


def collection_delete(request, pk, template_name='collection/collection_confirm_delete.html'):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(content='Authentication is required.')
    collection= get_object_or_404(Collection, pk=pk, user=request.user)    
    if request.method=='POST':
        collection.delete()
        return redirect('collection_list')
    return render(request, template_name, {'object':collection})


def _save_collection_form(request, form, template_name='collection/collection_form.html'):
    form.instance.user = request.user
    if form.is_valid():
        form.save()
        return redirect('collection_list')
    return render(request, template_name, {'form':form})
