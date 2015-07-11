import logging

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.views.generic import View

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

class UserDetailView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        roots = user.authority_set.filter(usage=Authority.ROOT)
        return render(request, "lacri/user_detail.html", {'user':user, 'roots':roots, 'form': CreateRootForm()})

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        roots = user.authority_set.filter(usage=Authority.ROOT)
        form = CreateRootForm(request.POST)
        if form.is_valid():
            common_name = form.cleaned_data['common_name']
            root = Authority(user=user, common_name=common_name, usage=Authority.ROOT)
            root.save()
            return HttpResponseRedirect(reverse('root_detail', kwargs={'username': username, 'root_slug': root.slug}))
        roots = user.authority_set.filter(usage=Authority.ROOT)
        return render(request, "lacri/user_detail.html", {'user':user, 'roots':roots, 'form': form})

class RootDetailView(View):
    def get(self, request, username, root_slug):
        user = get_object_or_404(User, username=username)
        root = get_object_or_404(Authority, user__username=username, slug=root_slug)
        site = Site.objects.get_current()
        domains = root.authority_set.filter(usage=Authority.DOMAIN)
        form = CreateDomainForm()
        return render(request, "lacri/root_detail.html", {'request': request, 'site': site, 'user':user, 'root': root, 'domains':domains, 'form': form})

    def post(self, request, username, root_slug):
        user = get_object_or_404(User, username=username)
        root = get_object_or_404(Authority, user__username=username, slug=root_slug)
        site = Site.objects.get_current()
        domains = root.authority_set.filter(usage=Authority.DOMAIN)
        form = CreateDomainForm(request.POST)
        if form.is_valid():
            common_name = form.cleaned_data['common_name']
            domain = Authority(user=user, common_name=common_name, parent=root, usage=Authority.DOMAIN)
            domain.save()
            return HttpResponseRedirect(reverse('domain_detail', kwargs={'username': username, 'root_slug': root.slug, 'domain': domain.common_name}))
        return render(request, "lacri/root_detail.html", {'request': request, 'site': site, 'user':user, 'root': root, 'domains':domains, 'form': form})

class RootCertPemView(View):
    def get(self, request, username, root_slug, ext):
        user = get_object_or_404(User, username=username)
        root = get_object_or_404(Authority, user__username=username, slug=root_slug)
        response = HttpResponse(content_type="application/x-pem-file")
        response.write(root.cert)
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

