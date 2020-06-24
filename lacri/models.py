import datetime
from io import StringIO
import logging
import hashlib

from django.db import models
from django.conf import settings
from django.template import Context, loader
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from .helpers import TarWriter
from OpenSSL import crypto

logger = logging.getLogger(__name__)

class Authority(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    common_name = models.CharField(max_length=256)
    slug = models.SlugField()
    key = models.TextField("Private key", blank=True)
    cert = models.TextField("Public certificate", blank=True)

    ROOT = 'R'
    DOMAIN = 'D'
    CLIENT = 'C'
    USAGE_CHOICES = (
        (ROOT, 'Root CA'),
        (DOMAIN, 'Domain'),
        (CLIENT, 'Client'),
    )
    usage = models.CharField(max_length=2, choices=USAGE_CHOICES, default=ROOT)

    class Meta:
        unique_together = (
            ("user", "slug"),
            ("user", "common_name"),
        )
        verbose_name= "Authority"
        verbose_name_plural = "Authorities"

    def save(self, *args, **kwargs):
        """
        Override the default save method to trigger generating/signing stuff
        the vpn service
        """
        logger.debug("saving %r" % self)
        self.slug = slugify(self.common_name)
        super(Authority, self).save(*args, **kwargs)
        if not all([self.key, self.cert]):
            self.generate()
            self.save()

    def generate(self):
        """
        Generate key & cert pair
        """
        # TODO: DoS protection
        # Generate key
        pkey = crypto.PKey()
        pkey.generate_key(crypto.TYPE_RSA, 2048)
        self.key = crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey, 'AES256', settings.SECRET_KEY.encode('utf-8'))
        # Make a signing request
        request = crypto.X509Req()
        subject = request.get_subject().CN = self.common_name
        request.set_pubkey(pkey)
        request.sign(pkey, 'sha256')
        # Make the certificate
        cert = crypto.X509()
        cert.set_serial_number(self.id)
        cert.set_version(2)
        cert.set_subject(request.get_subject())
        if self.usage == Authority.ROOT:
            cert.set_issuer(cert.get_subject())
        else:
            cert.set_issuer(self.parent._cert().get_subject())
        cert.set_pubkey(pkey)
        tenYears = datetime.timedelta(days=365*10)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(int(tenYears.total_seconds()))
        if self.usage == Authority.ROOT:
            cert.add_extensions([
                crypto.X509Extension(b'basicConstraints', False, b'CA:TRUE'),
                crypto.X509Extension(b'keyUsage', False, b'Certificate Sign, CRL Sign'),
                #crypto.X509Extension('subjectKeyIdentifier', b'hash'),
                #crypto.X509Extension('authorityKeyIdentifier', b'keyid,issuer:always'),
            ])
        elif self.usage == Authority.DOMAIN:
            cert.add_extensions([
                crypto.X509Extension(b'basicConstraints', False, b'CA:FALSE'),
                crypto.X509Extension(b'extendedKeyUsage', False, b'TLS Web Server Authentication'),
                crypto.X509Extension(b'keyUsage', False, b'Digital Signature, Key Encipherment'),
            ])
        elif self.usage == Authority.CLIENT:
            cert.add_extensions([
                crypto.X509Extension(b'basicConstraints', False, b'CA:FALSE'),
                crypto.X509Extension(b'extendedKeyUsage', False, b'TLS Web Client Authentication'),
                crypto.X509Extension(b'keyUsage', False, b'Digital Signature'),
            ])

        if self.usage == Authority.ROOT:
            cert.sign(pkey, 'sha256')
        else:
            cert.sign(self.parent._pkey(), 'sha256')

        self.cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)

    def write_cert_chain(self, fileobj):
        """
        Write a list of pem certs starting with this one and writing the
        parent below
        """
        fileobj.write(self.cert)
        if self.parent:
            self.parent.write_cert_chain(fileobj)

    def cert_chain(self):
        out = StringIO()
        self.write_cert_chain(out)
        return out.getvalue()

    def write_tar(self, fileobj):
        """
        Write a tar file containing the key and cert as typically needed by
        the server
        """
        try:
            tar = TarWriter(fileobj)
            tar.add("ssl/{self.common_name}.crt".format(self=self), self.cert_chain().encode('utf-8'))
            tar.add("ssl/{self.common_name}.key".format(self=self), self.key_decrypted().encode('utf-8'))
        except Exception as e:
            logger.error(str(e))
            raise

    def _pkey(self):
        return crypto.load_privatekey(crypto.FILETYPE_PEM, self.key, settings.SECRET_KEY.encode('utf-8'))

    def _cert(self):
        return crypto.load_certificate(crypto.FILETYPE_PEM, self.cert)

    def cert_fingerprint(self):
        return self._cert().digest('sha1').decode('utf-8')

    def key_fingerprint(self):
        return ""

    def key_decrypted(self):
        """
        Return a decrypted version of key
        """
        if not self.key:
            return ""
        return crypto.dump_privatekey(crypto.FILETYPE_PEM, self._pkey()).decode('utf-8')

    def __repr__(self):
        return "{0}('{self.common_name}', user=User('{self.user.username}'), usage='{self.usage}')".format(self.__class__.__name__, self=self)

    def __str__(self):
        return self.common_name
