from django.contrib import admin

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
            return "<b style='color:red'>{}</b>".format(str(e))
    def cert_as_text(self, network):
        try:
            return preformatted(network.cert_as_text())
        except Exception as e:
            return "<b style='color:red'>{}</b>".format(str(e))
    readonly_fields = ('cert_as_text', 'key_decrypted')
    #inlines = [ClientInline]
    #actions=[generate_pki, generate_client_certs]

admin.site.register(Authority, AuthorityAdmin)

