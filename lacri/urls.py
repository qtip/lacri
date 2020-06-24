from django.urls import re_path

from . import views

urlpatterns = [
    # e.g. /
    re_path(r'^$', views.IndexView.as_view(), name='index'),

    # e.g. /user/alice/
    re_path(r'^user/(?P<username>\w+)/$', views.UserDetailView.as_view(), name='user_detail'),

    # e.g. /user/alice/root/my-main-ca.crt
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).crt$', views.RootCertPemView.as_view(), name='root_cert_pem'),

    # e.g. /user/alice/root/my-main-ca.der
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).der$', views.RootCertDerView.as_view(), name='root_cert_der'),

    # e.g. /user/alice/root/my-main-ca.key
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).key$', views.RootKeyPemView.as_view(), name='root_key_pem'),

    # e.g. /user/alice/root/my-main-ca/
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/$', views.RootDetailView.as_view(), name='root_detail'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.chain.crt
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).chain.crt$', views.DomainCertChainPemView.as_view(), name='domain_cert_chain_pem'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.crt
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).crt$', views.DomainCertPemView.as_view(), name='domain_cert_pem'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.key
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).key$', views.DomainKeyPemView.as_view(), name='domain_key_pem'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.tar
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).tar$', views.DomainTarView.as_view(), name='domain_tar'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-])$', views.DomainDetailView.as_view(), name='domain_detail'),

]

