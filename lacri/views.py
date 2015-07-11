import logging

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.views.generic import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from .models import Authority
from .forms import CreateUserForm, CreateRootForm, CreateDomainForm

logger = logging.getLogger('lacri')

class IndexView(TemplateResponseMixin, View):
    template_name = "lacri/index.html"

    def get(self, request):
        return self.render_to_response({"form": CreateUserForm()})

    def post(self, request):
        form = CreateUserForm(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        # Display form validation errors
        return self.render_to_response({"form": form})

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is None:
            return self.user_not_found(form, username, password)
        else:
            return self.user_found(form, user)

    def user_found(self, form, user):
        if user.is_active:
            # User log in
            login(self.request, user)
            return HttpResponseRedirect(reverse('user_detail', kwargs={'username': user.username}))
        else:
            # User disabled error
            form.add_error('username', 'Account disabled')
            return self.render_to_response({"form": form})

    def user_not_found(self, form, username, password):
        try:
            # Create new user
            site = Site.objects.get_current()
            user = User.objects.create_user(username, '{}@{}'.format(username, site.domain), password)
            user.save()
            user = authenticate(username=username, password=password)
            login(self.request, user)
            return HttpResponseRedirect(reverse('user_detail', kwargs={'username': username}))
        except IntegrityError:
            # User already exists or Wrong password error
            form.add_error('username', 'Incorrect username/password')
            return self.render_to_response({"form": form})

class VerifyUserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.username != kwargs['username']:
            return HttpResponse('Unauthorized', status=401)
        return super(VerifyUserMixin, self).dispatch(request, *args, **kwargs)

class UserDetailView(VerifyUserMixin, TemplateResponseMixin, ContextMixin, View):
    template_name = "lacri/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        user = context['user'] = get_object_or_404(User, username=kwargs['username'])
        roots = context['roots'] = user.authority_set.filter(usage=Authority.ROOT)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context['form'] = CreateRootForm()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context['form'] = CreateRootForm(self.request.POST)
        if form.is_valid():
            common_name = form.cleaned_data['common_name']
            root = Authority(user=self.request.user, common_name=common_name, usage=Authority.ROOT)
            root.save()
            return HttpResponseRedirect(reverse('root_detail', kwargs={'username': kwargs['username'], 'root_slug': root.slug}))
        return self.render_to_response(context)

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
        form = context['form'] = CreateDomainForm()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context['form'] = CreateDomainForm(request.POST)
        if form.is_valid():
            common_name = form.cleaned_data['common_name']
            domain = Authority(user=context['user'], common_name=common_name, parent=context['root'], usage=Authority.DOMAIN)
            domain.save()
            return HttpResponseRedirect(reverse('domain_detail', kwargs={'username': kwargs['username'], 'root_slug': kwargs['root_slug'], 'domain': domain.common_name}))
        return self.render_to_response(context)

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

class DomainCertDerView(DomainDetailBase):
    def get(self, request, *args, **kwargs):
        content_type="application/x-x509-ca-cert"
        raise NotImplementedError()

class DomainTarView(VerifyUserMixin, DomainDetailBase):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = HttpResponse(content_type="application/x-tar")
        context['domain'].write_tar(response)
        return response

