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
from M2Crypto import RSA, X509, EVP, m2, Rand, Err, ASN1, DH, BIO

logger = logging.getLogger(__name__)

class Authority(models.Model):
    user = models.ForeignKey(User)
    parent = models.ForeignKey('self', null=True, blank=True)
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
        # replace this with pulling from an RSA queue for performance
        rsa_key = RSA.gen_key(2048, m2.RSA_F4, callback=lambda: None)
        key = EVP.PKey()
        key.assign_rsa(rsa_key)
        self.key = key.as_pem(callback=lambda x: settings.SECRET_KEY)
        request = X509.Request()
        request.set_version(2)
        request.set_pubkey(key)
        request_subject_name = X509.X509_Name()
        request_subject_name.CN = self.common_name
        request.set_subject_name(request_subject_name)
        request.sign(key, 'sha256')
        cert = X509.X509()
        cert.set_serial_number(self.id)
        cert.set_version(2)
        cert.set_subject(request.get_subject())
        cert_issuer_name = X509.X509_Name()
        if self.usage == Authority.ROOT:
            cert_issuer_name.CN = self.common_name
        else:
            cert_issuer_name.CN = self.parent.common_name
        cert.set_issuer(cert_issuer_name)
        cert.set_pubkey(key)
        now = ASN1.ASN1_UTCTIME()
        now.set_datetime(datetime.datetime.now())
        nowPlusTenYears = ASN1.ASN1_UTCTIME()
        nowPlusTenYears.set_datetime(datetime.datetime.now() + datetime.timedelta(days=365*10))
        cert.set_not_before(now)
        cert.set_not_after(nowPlusTenYears)
        if self.usage == Authority.ROOT:
            cert.add_ext(X509.new_extension('basicConstraints', 'CA:TRUE'))
            cert.add_ext(X509.new_extension('keyUsage', 'Certificate Sign, CRL Sign'))
            #cert.add_ext(X509.new_extension('subjectKeyIdentifier', 'hash'))
            #cert.add_ext(X509.new_extension('authorityKeyIdentifier', 'keyid,issuer:always'))
        elif self.usage == Authority.DOMAIN:
            cert.add_ext(X509.new_extension('basicConstraints', 'CA:FALSE'))
            cert.add_ext(X509.new_extension('extendedKeyUsage', 'TLS Web Server Authentication'))
            cert.add_ext(X509.new_extension('keyUsage', 'Digital Signature, Key Encipherment'))
            # should the root have this also?
            cert.set_subject(request.get_subject())
            cert.set_pubkey(request.get_pubkey())
        elif self.usage == Authority.CLIENT:
            cert.add_ext(X509.new_extension('basicConstraints', 'CA:FALSE'))
            cert.add_ext(X509.new_extension('extendedKeyUsage', 'TLS Web Client Authentication'))
            cert.add_ext(X509.new_extension('keyUsage', 'Digital Signature'))
            # should the root have this also?
            cert.set_subject(request.get_subject())
            cert.set_pubkey(request.get_pubkey())

        if self.usage == Authority.ROOT:
            # sign the cert with its own key
            cert.sign(key, 'sha256')
        else:
            # sign the cert with the root key
            cert.sign(self.parent._pkey(), 'sha256')
        self.cert = cert.as_pem()

    def cert_as_text(self):
        """
        Return a plain-text human readable version of the cert
        """
        if not self.cert:
            return ""
        return X509.load_cert_string(str(self.cert)).as_text()

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
            tar.add("ssl/{self.common_name}.crt".format(self=self), self.cert_chain())
            tar.add("ssl/{self.common_name}.key".format(self=self), self.key_decrypted())
        except Exception as e:
            logger.error(str(e))
            raise

    def _pkey(self):
        return EVP.load_key_string(str(self.key), callback=lambda x: settings.SECRET_KEY)

    def key_decrypted(self):
        """
        Return a decrypted version of key
        """
        if not self.key:
            return ""
        return self._pkey().as_pem(cipher=None)

    def __repr__(self):
        return "{0}('{self.common_name}', user=User('{self.user.username}'), usage='{self.usage}')".format(self.__class__.__name__, self=self)

    def __unicode__(self):
        return self.common_name
