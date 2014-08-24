from django.http import Http404
from django.shortcuts import render_to_response

from .models import Webpage


def default_webpage_view(request, path):
    try:
        webpage = Webpage.objects.get(
            domain__domain=request.META['HTTP_HOST'],
            path=path,
        )
    except Webpage.DoesNotExist:
        raise Http404()
    return render_to_response(
        'server/default.html',
        {
            'webpage': webpage,
        },
    )
