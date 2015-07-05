from django import template

register = template.Library()

@register.filter(name='cidr2mask')
def cidr2mask(value):
    addr, bits = value.split("/")
    return addr, '.'.join(str(256-2**(8-min(max(0, int(bits)-8*n), 8))) for n in range(4))
