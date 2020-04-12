from django.shortcuts import redirect, reverse


def do_delete_share(share):
    share.delete()
    url = reverse('share-log')
    return redirect(url)
