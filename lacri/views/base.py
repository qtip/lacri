import logging

from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.views.generic import View, TemplateView
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from ..models import Authority
from ..forms import CreateUserForm, CreateRootForm

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

class AuthorityView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(AuthorityView, self).get_context_data(**kwargs)
        user = context['user'] = get_object_or_404(User, username=kwargs['username'])
        roots = context['roots'] = user.authority_set.filter(usage=Authority.ROOT)

        if 'slug' in kwargs and 'common_name' in kwargs:
            authority = context['authority'] = user.authority_set.filter(
                parent__slug=kwargs['slug'],
                common_name=kwargs['common_name'],
            )
        elif 'slug' in kwargs:
            authority = context['authority'] = user.authority_set.filter(slug=kwargs['slug'])

        if authority:
            children = context['children'] = user.authority_set.filter(parent=authority).order_by('usage')
            domains = context['domains'] = children.filter(usage=Authority.DOMAIN)
            clients = context['clients'] = children.filter(usage=Authority.CLIENT)

        return context

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
