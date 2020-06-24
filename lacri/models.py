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
from cryptography import x509
from cryptography.x509 import NameOID
from cryptography.x509.extensions import KeyUsage
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

logger = logging.getLogger(__name__)

class Authority(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
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
        adding = self._state.adding
        self.slug = slugify(self.common_name)
        super().save(*args, **kwargs)
        if not all([self.key, self.cert]):
            try:
                self.generate()
                self.save()
            except:
                if adding:
                    self.delete()
                raise

    def generate(self):
        """
        Generate key & cert pair
        """
        # TODO: DoS protection
        # Generate key
        pkey = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        self.key = pkey.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(settings.SECRET_KEY.encode('utf-8'))
        ).decode('utf-8')

        # Set up the name
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, self.common_name)])

        # Make a signing request
        csr_builder = x509.CertificateSigningRequestBuilder()
        csr_builder = csr_builder.subject_name(name)
        csr = csr_builder.sign(pkey, hashes.SHA256(), default_backend())

        # Make the certificate
        cert_builder = x509.CertificateBuilder()
        cert_builder = cert_builder.subject_name(name)
        cert_builder = cert_builder.public_key(pkey.public_key())
        cert_builder = cert_builder.serial_number(self.id)
        cert_builder = cert_builder.not_valid_before(datetime.datetime.utcnow())
        cert_builder = cert_builder.add_extension(KeyUsage(
            digital_signature = self.usage in (Authority.DOMAIN, Authority.CLIENT),
            content_commitment = False,
            key_encipherment = self.usage == Authority.DOMAIN,
            data_encipherment = False,
            key_agreement = False,
            key_cert_sign = self.usage == Authority.ROOT,
            crl_sign = self.usage == Authority.ROOT,
            encipher_only = False,
            decipher_only = False,
        ), critical=False)
        if self.usage == Authority.ROOT:
            cert_builder = cert_builder.issuer_name(name)
            cert = cert_builder.sign(pkey, hashes.SHA256(), default_backend())
        else:
            cert_builder = cert_builder.issuer_name(self.parent._cert().subject)
            cert = cert_builder.sign(self.parent._pkey(), hashes.SHA256(), default_backend())


        self.cert = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
        return

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
        return serialization.load_pem_private_key(
                self.key.encode('utf-8'),
                password=settings.SECRET_KEY.encode('utf-8'),
                backend=default_backend(),
        )

    def _cert(self):
        return x509.load_pem_x509_certificate(self.cert.encode('utf-8'), default_backend())

    def cert_fingerprint(self):
        return self._cert().fingerprint(hashes.SHA256()).hex()

    def key_fingerprint(self):
        return ""

    def key_decrypted(self):
        """
        Return a decrypted version of key
        """
        if not self.key:
            return ""
        return self._pkey().private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
        ).decode('utf-8')

    def __repr__(self):
        return "{0}('{self.common_name}', user=User('{self.user.username}'), usage='{self.usage}')".format(self.__class__.__name__, self=self)

    def __str__(self):
        return self.common_name
