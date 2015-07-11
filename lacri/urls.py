from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    # e.g. /
    url(r'^$', views.IndexView.as_view(), name='index'),

    # e.g. /user/alice/
    url(r'^user/(?P<username>\w+)/$', views.UserDetailView.as_view(), name='user_detail'),

    # e.g. /user/alice/root/my-main-ca.pem
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).(?P<ext>crt|pem)$', views.RootCertPemView.as_view(), name='root_cert_pem'),

    # e.g. /user/alice/root/my-main-ca.der
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).der$', views.RootCertDerView.as_view(), name='root_cert_der'),

    # e.g. /user/alice/root/my-main-ca.key
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).key$', views.RootKeyPemView.as_view(), name='root_key_pem'),

    # e.g. /user/alice/root/my-main-ca/
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/$', views.RootDetailView.as_view(), name='root_detail'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.tar
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).tar$', views.DomainTarView.as_view(), name='domain_tar'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.crt
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).(?P<ext>crt|pem)$', views.DomainCertPemView.as_view(), name='domain_cert_pem'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-])$', views.DomainDetailView.as_view(), name='domain_detail'),

)

