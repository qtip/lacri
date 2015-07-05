from django.contrib import admin
from django.utils.safestring import mark_safe, mark_for_escaping

from lacri.models import Authority

def preformatted(value):
    if not value:
        return value
    return "<br/><pre>"+value+"</pre>"

class AuthorityAdmin(admin.ModelAdmin):
    def key_decrypted(self, network):
        try:
            return preformatted(network.key_decrypted())
        except Exception as e:
            return u"<b style='color:red'>{}</b>".format(unicode(e))
    def cert_as_text(self, network):
        try:
            return preformatted(network.cert_as_text())
        except Exception as e:
            return u"<b style='color:red'>{}</b>".format(unicode(e))
    readonly_fields = ('cert_as_text', 'key_decrypted')
    #inlines = [ClientInline]
    #actions=[generate_pki, generate_client_certs]

admin.site.register(Authority, AuthorityAdmin)

