from django.conf.urls import patterns, url

from .views import base, root, domain

urlpatterns = patterns('',
    # e.g. /
    url(r'^$', base.IndexView.as_view(), name='index'),

    # e.g. /user/alice/
    url(r'^user/(?P<username>\w+)/$', base.UserDetailView.as_view(), name='user_detail'),

    # e.g. /user/alice/root/my-main-ca.crt
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).crt$', root.RootCertPemView.as_view(), name='root_cert_pem'),

    # e.g. /user/alice/root/my-main-ca.der
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).der$', root.RootCertDerView.as_view(), name='root_cert_der'),

    # e.g. /user/alice/root/my-main-ca.key
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).key$', root.RootKeyPemView.as_view(), name='root_key_pem'),

    # e.g. /user/alice/root/my-main-ca/
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/$', root.RootDetailView.as_view(), name='root_detail'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.chain.crt
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).chain.crt$', 
        domain.DomainCertChainPemView.as_view(), name='domain_cert_chain_pem'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.crt
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).crt$',
        domain.DomainCertPemView.as_view(), name='domain_cert_pem'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.key
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).key$',
        domain.DomainKeyPemView.as_view(), name='domain_key_pem'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.tar
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).tar$',
        domain.DomainTarView.as_view(), name='domain_tar'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-])$',
        domain.DomainDetailView.as_view(), name='domain_detail'),

)

