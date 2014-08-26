from django.http import Http404
from django.core.context_processors import csrf
from django.shortcuts import render_to_response

from server.models import Domain, Webpage

from .generator import generate


def domain_list_view(request):
    domains = Domain.objects.all()
    return render_to_response(
        'generator/domain_list.html',
        {
            'domains': domains,
        },
    )


def domain_view(request, **kwargs):
    try:
        domain = Domain.objects.get(domain=kwargs['domain'])
    except Domain.DoesNotExist:
        raise Http404
    webpages = Webpage.objects.filter(domain=domain)
    return render_to_response(
        'generator/domain.html',
        {
            'domain': domain,
            'webpages': webpages,
        },
    )


def generator_view(request):
    context = {}
    context.update(csrf(request))
    if request.method == 'POST':
        generate(
            50,  # domain count
            request.POST.get('page'),  # start url
            20  # crawl limit
        )
    return render_to_response(
        'generator/generator.html',
        context,
    )
