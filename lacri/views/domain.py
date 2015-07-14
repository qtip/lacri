import logging

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.generic import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from ..models import Authority
from .base import VerifyUserMixin

logger = logging.getLogger('lacri')

class DomainDetailBase(ContextMixin, View):
    def get_context_data(self, **kwargs):
        context = super(DomainDetailBase, self).get_context_data(**kwargs)
        site = context['site'] = Site.objects.get_current()
        user = context['user'] = get_object_or_404(User, username=kwargs['username'])
        root = context['root'] = user.authority_set.filter(usage=Authority.ROOT, slug=kwargs['root_slug']).get()
        domain = context['domain'] = root.authority_set.filter(usage=Authority.DOMAIN, parent=root, common_name=kwargs['domain']).get()
        return context

class DomainDetailView(TemplateResponseMixin, VerifyUserMixin, DomainDetailBase):
    template_name = "lacri/domain_detail.html"

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

class DomainCertPemView(DomainDetailBase):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = HttpResponse(content_type="application/x-pem-file")
        response.write(context['domain'].cert)
        return response

class DomainCertChainPemView(DomainDetailBase):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = HttpResponse(content_type="application/x-pem-file")
        context['domain'].write_cert_chain(response)
        return response

class DomainCertDerView(DomainDetailBase):
    def get(self, request, *args, **kwargs):
        content_type="application/x-x509-ca-cert"
        raise NotImplementedError()

class DomainKeyPemView(VerifyUserMixin, DomainDetailBase):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = HttpResponse(content_type="application/x-pem-file")
        response.write(context['domain'].key_decrypted())
        return response

class DomainTarView(VerifyUserMixin, DomainDetailBase):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = HttpResponse(content_type="application/x-tar")
        context['domain'].write_tar(response)
        return response

