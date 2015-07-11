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

class IndexView(View):
    def get(self, request):
        return render(request, "lacri/index.html", {"form": CreateUserForm()})

    def post(self, request):
        form = CreateUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('user_detail', kwargs={'username': username}))
                else:
                    # disabled account
                    pass
            else:
                try:
                    site = Site.objects.get_current()
                    user = User.objects.create_user(username, '{}@{}'.format(username, site.domain), password)
                    user.save()
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    return HttpResponseRedirect(reverse('user_detail', kwargs={'username': username}))
                except IntegrityError:
                    form.add_error('username', 'Incorrect username/password')
        return render(request, "lacri/index.html", {"form": form})

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

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context['form'] = CreateRootForm()
        return self.render_to_response(context)

    def post(self, *args, **kwargs):
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

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context['form'] = CreateDomainForm()
        return self.render_to_response(context)

    def post(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context['form'] = CreateDomainForm(request.POST)
        if form.is_valid():
            common_name = form.cleaned_data['common_name']
            domain = Authority(user=user, common_name=common_name, parent=root, usage=Authority.DOMAIN)
            domain.save()
            return HttpResponseRedirect(reverse('domain_detail', kwargs={'username': kwargs['username'], 'root_slug': kwargs['root_slug'], 'domain': domain.common_name}))
        return self.render_to_response(context)

class RootCertPemView(RootDetailBase):
    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = HttpResponse(content_type="application/x-pem-file")
        response.write(context['root'].cert)
        return response

class RootCertDerView(View):
    def get(self, request, username, root_slug):
        content_type="application/x-x509-ca-cert"
        raise NotImplementedError()

class DomainDetailView(View):
    def get(self, request, username, root_slug, domain):
        site = Site.objects.get_current()
        user = get_object_or_404(User, username=username)
        root = get_object_or_404(Authority, user__username=username, slug=root_slug)
        domain = root.authority_set.filter(usage=Authority.DOMAIN, parent=root, common_name=domain).get()
        return render(request, "lacri/domain_detail.html", {'request': request, 'site': site, 'user':user, 'root': root, 'domain':domain})

class DomainCertPemView(View):
    def get(self, request, username, root_slug, domain, ext):
        user = get_object_or_404(User, username=username)
        root = get_object_or_404(Authority, user__username=username, slug=root_slug)
        domain = root.authority_set.filter(usage=Authority.DOMAIN, parent=root, common_name=domain).get()
        response = HttpResponse(content_type="application/x-pem-file")
        response.write(domain.cert)
        return response

class DomainTarView(View):
    def get(self, request, username, root_slug, domain):
        user = get_object_or_404(User, username=username)
        root = get_object_or_404(Authority, user__username=username, slug=root_slug)
        domain = root.authority_set.filter(usage=Authority.DOMAIN, parent=root, common_name=domain).get()
        response = HttpResponse(content_type="application/x-tar")
        domain.write_tar(response)
        return response

