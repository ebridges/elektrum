from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from django.http import HttpResponseForbidden

from albums.models import Album


class AlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = ['path', 'collection']


def album_list(request, collection, template_name='album/album_list.html'):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(content='Authentication is required.')
    album = Album.objects.filter(user=request.user, collection=collection)
    data = {'object_list': album}
    return render(request, template_name, data)


def album_view(request, pk, template_name='album/album_detail.html'):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(content='Authentication is required.')
    album = get_object_or_404(Album, pk=pk, user=request.user)
    return render(request, template_name, {'object': album})


def album_create(request, template_name='album/album_form.html'):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(content='Authentication is required.')
    form = AlbumForm(request.POST or None)
    return _save_album_form(request, form, template_name)


def album_edit(request, pk, template_name='album/album_form.html'):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(content='Authentication is required.')
    album = get_object_or_404(Album, pk=pk, user=request.user)
    form = AlbumForm(request.POST or None, instance=album)
    return _save_album_form(request, form, template_name)


def album_delete(request, pk, template_name='album/album_confirm_delete.html'):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(content='Authentication is required.')
    album = get_object_or_404(Album, pk=pk, user=request.user)
    if request.method == 'POST':
        album.delete()
        return redirect('album_list')
    return render(request, template_name, {'object': album})


def _save_album_form(request, form, template_name):
    form.instance.user = request.user
    if form.is_valid():
        form.save()
        return redirect('album_list')
    return render(request, template_name, {'form': form})
