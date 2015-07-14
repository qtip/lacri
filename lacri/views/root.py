import logging

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from ..models import Authority
from ..forms import CreateDomainForm, CreateClientForm
from ..helpers import create_form
from .base import VerifyUserMixin

logger = logging.getLogger('lacri')

class RootDetailBase(ContextMixin, View):
    def get_context_data(self, **kwargs):
        context = super(RootDetailBase, self).get_context_data(**kwargs)
        site = context['site'] = Site.objects.get_current()
        user = context['user'] = get_object_or_404(User, username=kwargs['username'])
        root = context['root'] = user.authority_set.filter(slug=kwargs['root_slug']).get()
        domains = context['domains'] = user.authority_set.filter(usage=Authority.DOMAIN, parent=root)
        return context

class RootDetailView(TemplateResponseMixin, VerifyUserMixin, RootDetailBase):
    template_name = "lacri/root_detail.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        domain_form = context['domain_form'] = CreateDomainForm(prefix="domain")
        client_form = context['client_form'] = CreateClientForm(prefix="client")
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        domain_form = context['domain_form'] = create_form(CreateDomainForm, request, prefix='domain')
        client_form = context['client_form'] = create_form(CreateClientForm, request, prefix='client')
        if domain_form.is_bound and domain_form.is_valid():
            return self.domain_form_valid(domain_form, context)
        if client_form.is_bound and client_form.is_valid():
            return self.client_form_valid(client_form, context)
        return self.render_to_response(context)

    def domain_form_valid(self, form, context):
        common_name = form.cleaned_data['common_name']
        domain = Authority(user=context['user'], common_name=common_name, parent=context['root'], usage=Authority.DOMAIN)
        domain.save()
        return HttpResponseRedirect(reverse('domain_detail', kwargs={'username': context['username'], 'root_slug': context['root_slug'], 'domain': domain.common_name}))

    def client_form_valid(self, form, context):
        common_name = form.cleaned_data['common_name']
        client = Authority(user=context['user'], common_name=common_name, parent=context['root'], usage=Authority.CLIENT)
        client.save()
        return HttpResponseRedirect(reverse('client_detail', kwargs={'username': context['username'], 'root_slug': context['root_slug'], 'client': client.common_name}))

class RootCertPemView(RootDetailBase):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = HttpResponse(content_type="application/x-pem-file")
        response.write(context['root'].cert)
        return response

class RootKeyPemView(VerifyUserMixin, RootDetailBase):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = HttpResponse(content_type="application/x-pem-file")
        response.write(context['root'].key_decrypted())
        return response

class RootCertDerView(View):
    def get(self, request, *args, **kwargs):
        content_type="application/x-x509-ca-cert"
        raise NotImplementedError()
