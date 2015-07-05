from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    # e.g. /
    url(r'^$', views.index, name='index'),

    # e.g. /user/alice/
    url(r'^user/(?P<username>\w+)/$', views.user_detail, name='user_detail'),

    # e.g. /user/alice/root/
    #url(r'^user/(?P<username>\w+)/root/$', views.roots, name='roots'),

    # e.g. /user/alice/root/my-main-ca.pem
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+).pem$', views.root_pem, name='root_pem'),

    # e.g. /user/alice/root/my-main-ca/
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/$', views.root_detail, name='root_detail'),

    # e.g. /user/alice/root/my-main-ca/domain/
    #url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/$', views.domains, name='domains'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.tar
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).tar$', views.domain_tar, name='domain_tar'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com.crt
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-]).crt$', views.domain_cert, name='domain_cert'),

    # e.g. /user/alice/root/my-main-ca/domain/*.alice.com
    url(r'^user/(?P<username>\w+)/root/(?P<root_slug>[\w_-]+)/domain/(?P<domain>(\*\.)?[\w\-\.]*[\w\-])$', views.domain_detail, name='domain_detail'),



    # client certs
    # ------------

    # e.g. /user/alice/root/*.alice.com/client/

    # e.g. /user/alice/root/*.alice.com/client/bob

    # e.g. /user/alice/root/*.alice.com/client/bob.crt

    # OpenVPN config
    # --------------

    # e.g. /user/alice/root/*.alice.com/ovpn/

    # e.g. /user/alice/root/*.alice.com/ovpn/config.tar

    # e.g. /user/alice/root/*.alice.com/client/bob/ovpn/bob-desktop.ovpn
)
