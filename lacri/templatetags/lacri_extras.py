from django import template
from django.urls import reverse
from ..models import Authority

register = template.Library()

@register.filter(name='cidr2mask')
def cidr2mask(value):
    addr, bits = value.split("/")
    return addr, '.'.join(str(256-2**(8-min(max(0, int(bits)-8*n), 8))) for n in range(4))


@register.filter(name='authority_detail_url')
def authority_detail_url(authority):
    usage = authority.usage
    if usage == Authority.ROOT:
        return reverse('new_root_detail', kwargs={
            'username': authority.user.username,
            'slug': authority.slug
        })
    elif usage == Authority.DOMAIN:
        return reverse('domain_detail', kwargs={
            'username': authority.user.username,
            'root_slug': authority.parent.slug,
            'domain': authority.common_name,
        })
    elif usage == Authority.CLIENT:
        return reverse('client_detail', kwargs={
            'username': authority.user.username,
            'root_slug': authority.parent.slug,
            'client': authority.slug,
        })

@register.filter(name='usage_to_str')
def usage_to_str(usage):
    if usage == Authority.ROOT: 
        return "Root"
    elif usage == Authority.DOMAIN: 
        return "Domain"
    elif usage == Authority.CLIENT: 
        return "Client"

