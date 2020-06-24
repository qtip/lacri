from django.urls import re_path
from .views import base, root, domain, client

urlpatterns = [
    # e.g. /
    re_path(r'^$', base.IndexView.as_view(), name='index'),

    # e.g. /user/alice/
    re_path(r'^user/(?P<username>\w+)/$', base.UserDetailView.as_view(), name='user_detail'),

    # e.g. /user/alice/root/my-main-ca.crt
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).crt$', root.RootCertPemView.as_view(), name='root_cert_pem'),

    # e.g. /user/alice/root/my-main-ca.der
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).der$', root.RootCertDerView.as_view(), name='root_cert_der'),

    # e.g. /user/alice/root/my-main-ca.key
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).key$', root.RootKeyPemView.as_view(), name='root_key_pem'),

    # e.g. /user/alice/root/my-main-ca/
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/$', root.RootDetailView.as_view(), name='root_detail'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.chain.crt
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).chain.crt$', 
        domain.DomainCertChainPemView.as_view(), name='domain_cert_chain_pem'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.crt
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).crt$',
        domain.DomainCertPemView.as_view(), name='domain_cert_pem'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.key
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).key$',
        domain.DomainKeyPemView.as_view(), name='domain_key_pem'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.tar
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).tar$',
        domain.DomainTarView.as_view(), name='domain_tar'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-])$',
        domain.DomainDetailView.as_view(), name='domain_detail'),

    # e.g. /user/alice/root/my-main-ca/client/???
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/client/(?P<client>[^/]+)$',
        client.ClientDetailView.as_view(), name='client_detail'),

    # e.g. /user/alice/root/my-main-ca/client/*.alice.com.chain.crt
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/client/(?P<client>(\*\.)?[\w\-\.]*[\w\-]).chain.crt$', 
        client.ClientCertChainPemView.as_view(), name='client_cert_chain_pem'),

    # e.g. /user/alice/root/my-main-ca/client/*.alice.com.crt
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/client/(?P<client>(\*\.)?[\w\-\.]*[\w\-]).crt$',
        client.ClientCertPemView.as_view(), name='client_cert_pem'),

    # e.g. /user/alice/root/my-main-ca/client/*.alice.com.key
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/client/(?P<client>(\*\.)?[\w\-\.]*[\w\-]).key$',
        client.ClientKeyPemView.as_view(), name='client_key_pem'),

    # e.g. /user/alice/root/my-main-ca/client/*.alice.com.tar
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/client/(?P<client>(\*\.)?[\w\-\.]*[\w\-]).tar$',
        client.ClientTarView.as_view(), name='client_tar'),

    # e.g. /user/alice/root/my-main-ca/client/*.alice.com
    re_path(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/client/(?P<client>(\*\.)?[\w\-\.]*[\w\-])$',
        client.ClientDetailView.as_view(), name='client_detail'),
]

