import logging

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.db import IntegrityError

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from .models import Authority
from .forms import CreateUserForm, CreateRootForm, CreateDomainForm

logger = logging.getLogger('lacri')

def index(request):
    if request.method == "POST":
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
    else: # GET
        form = CreateUserForm()
    return render(request, "lacri/index.html", {"form": form})

def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = CreateRootForm(request.POST)
        if form.is_valid():
            common_name = form.cleaned_data['common_name']
            root = Authority(user=user, common_name=common_name, usage=Authority.ROOT)
            root.save()
            return HttpResponseRedirect(reverse('root_detail', kwargs={'username': username, 'root_slug': root.slug}))
    else:
        form = CreateRootForm()
    roots = user.authority_set.filter(usage=Authority.ROOT)
    return render(request, "lacri/user_detail.html", {'user':user, 'roots':roots, 'form': form})

#def roots(request, username):
    #user = get_object_or_404(User, username=username)
    #roots = user.authority_set.filter(usage=Authority.ROOT)
    #return render(request, "lacri/roots.html", {'roots':roots})

def root_detail(request, username, root_slug):
    user = get_object_or_404(User, username=username)
    root = get_object_or_404(Authority, user__username=username, slug=root_slug)
    if request.method == 'POST':
        form = CreateDomainForm(request.POST)
        if form.is_valid():
            common_name = form.cleaned_data['common_name']
            domain = Authority(user=user, common_name=common_name, parent=root, usage=Authority.DOMAIN)
            domain.save()
            return HttpResponseRedirect(reverse('domain_detail', kwargs={'username': username, 'root_slug': root.slug, 'domain': domain.common_name}))
    else:
        form = CreateDomainForm()
    site = Site.objects.get_current()
    domains = root.authority_set.filter(usage=Authority.DOMAIN)
    return render(request, "lacri/root_detail.html", {'site': site, 'user':user, 'root': root, 'domains':domains, 'form': form})

def root_pem(request, username, root_slug):
    user = get_object_or_404(User, username=username)
    root = get_object_or_404(Authority, user__username=username, slug=root_slug)
    response = HttpResponse(content_type="application/x-pem-file")
    response.write(root.cert)
    return response


#def domains(request, username, root_slug):
    #return HttpResponse("ohai user " + username + ", here're your domains for " + root_slug)

def domain_detail(request, username, root_slug, domain):
    site = Site.objects.get_current()
    user = get_object_or_404(User, username=username)
    root = get_object_or_404(Authority, user__username=username, slug=root_slug)
    domain = root.authority_set.filter(usage=Authority.DOMAIN, parent=root, common_name=domain).get()
    return render(request, "lacri/domain_detail.html", {'site': site, 'user':user, 'root': root, 'domain':domain})

def domain_cert(request, username, root_slug, domain):
    return "asdf"

def domain_tar(request, username, root_slug, domain):
    user = get_object_or_404(User, username=username)
    root = get_object_or_404(Authority, user__username=username, slug=root_slug)
    domain = root.authority_set.filter(usage=Authority.DOMAIN, parent=root, common_name=domain).get()
    response = HttpResponse(content_type="application/x-tar")
    domain.write_tar(response)
    return response

#def client_ovpn(request, username, network_slug, client_slug):
    #client = get_object_or_404(Client, network__user__username=username, network__slug=network_slug, slug=client_slug)
    #response = HttpResponse(content_type="application/octet-stream")
    #response.write(client.ovpn_conf())
    #return response
