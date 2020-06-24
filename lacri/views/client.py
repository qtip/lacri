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

class ClientDetailBase(ContextMixin, View):
    def get_context_data(self, **kwargs):
        context = super(ClientDetailBase, self).get_context_data(**kwargs)
        site = context['site'] = Site.objects.get_current()
        user = context['user'] = get_object_or_404(User, username=kwargs['username'])
        root = context['root'] = user.authority_set.filter(usage=Authority.ROOT, slug=kwargs['root_slug']).get()
        client = context['client'] = root.authority_set.filter(usage=Authority.CLIENT, parent=root, common_name=kwargs['client']).get()
        return context

class ClientDetailView(TemplateResponseMixin, VerifyUserMixin, ClientDetailBase):
    template_name = "lacri/client_detail.html"

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

class ClientCertPemView(ClientDetailBase):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = HttpResponse(content_type="application/x-pem-file")
        response.write(context['client'].cert)
        return response

class ClientCertChainPemView(ClientDetailBase):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = HttpResponse(content_type="application/x-pem-file")
        context['client'].write_cert_chain(response)
        return response

class ClientCertDerView(ClientDetailBase):
    def get(self, request, *args, **kwargs):
        content_type="application/x-x509-ca-cert"
        raise NotImplementedError()

class ClientKeyPemView(VerifyUserMixin, ClientDetailBase):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = HttpResponse(content_type="application/x-pem-file")
        response.write(context['client'].key_decrypted())
        return response

class ClientTarView(VerifyUserMixin, ClientDetailBase):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = HttpResponse(content_type="application/x-tar")
        context['client'].write_tar(response)
        return response

