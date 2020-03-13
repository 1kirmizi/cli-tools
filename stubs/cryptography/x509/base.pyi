# Stubs for cryptography.x509.base (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

import abc
from enum import Enum
from typing import Any, Optional

class Version(Enum):
    v1: int = ...
    v3: int = ...

def load_pem_x509_certificate(data: Any, backend: Any): ...
def load_der_x509_certificate(data: Any, backend: Any): ...
def load_pem_x509_csr(data: Any, backend: Any): ...
def load_der_x509_csr(data: Any, backend: Any): ...
def load_pem_x509_crl(data: Any, backend: Any): ...
def load_der_x509_crl(data: Any, backend: Any): ...

class InvalidVersion(Exception):
    parsed_version: Any = ...
    def __init__(self, msg: Any, parsed_version: Any) -> None: ...

class Certificate(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def fingerprint(self, algorithm: Any) -> Any: ...
    def serial_number(self) -> Any: ...
    def version(self) -> Any: ...
    @abc.abstractmethod
    def public_key(self) -> Any: ...
    def not_valid_before(self) -> Any: ...
    def not_valid_after(self) -> Any: ...
    def issuer(self) -> Any: ...
    def subject(self) -> Any: ...
    def signature_hash_algorithm(self) -> Any: ...
    def signature_algorithm_oid(self) -> Any: ...
    def extensions(self) -> Any: ...
    def signature(self) -> Any: ...
    def tbs_certificate_bytes(self) -> Any: ...
    @abc.abstractmethod
    def __eq__(self, other: Any) -> Any: ...
    @abc.abstractmethod
    def __ne__(self, other: Any) -> Any: ...
    @abc.abstractmethod
    def __hash__(self) -> Any: ...
    @abc.abstractmethod
    def public_bytes(self, encoding: Any) -> Any: ...

class CertificateRevocationList(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def public_bytes(self, encoding: Any) -> Any: ...
    @abc.abstractmethod
    def fingerprint(self, algorithm: Any) -> Any: ...
    @abc.abstractmethod
    def get_revoked_certificate_by_serial_number(self, serial_number: Any) -> Any: ...
    def signature_hash_algorithm(self) -> Any: ...
    def signature_algorithm_oid(self) -> Any: ...
    def issuer(self) -> Any: ...
    def next_update(self) -> Any: ...
    def last_update(self) -> Any: ...
    def extensions(self) -> Any: ...
    def signature(self) -> Any: ...
    def tbs_certlist_bytes(self) -> Any: ...
    @abc.abstractmethod
    def __eq__(self, other: Any) -> Any: ...
    @abc.abstractmethod
    def __ne__(self, other: Any) -> Any: ...
    @abc.abstractmethod
    def __len__(self) -> Any: ...
    @abc.abstractmethod
    def __getitem__(self, idx: Any) -> Any: ...
    @abc.abstractmethod
    def __iter__(self) -> Any: ...
    @abc.abstractmethod
    def is_signature_valid(self, public_key: Any) -> Any: ...

class CertificateSigningRequest(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __eq__(self, other: Any) -> Any: ...
    @abc.abstractmethod
    def __ne__(self, other: Any) -> Any: ...
    @abc.abstractmethod
    def __hash__(self) -> Any: ...
    @abc.abstractmethod
    def public_key(self) -> Any: ...
    def subject(self) -> Any: ...
    def signature_hash_algorithm(self) -> Any: ...
    def signature_algorithm_oid(self) -> Any: ...
    def extensions(self) -> Any: ...
    @abc.abstractmethod
    def public_bytes(self, encoding: Any) -> Any: ...
    def signature(self) -> Any: ...
    def tbs_certrequest_bytes(self) -> Any: ...
    def is_signature_valid(self) -> Any: ...

class RevokedCertificate(metaclass=abc.ABCMeta):
    def serial_number(self) -> Any: ...
    def revocation_date(self) -> Any: ...
    def extensions(self) -> Any: ...

class CertificateSigningRequestBuilder:
    def __init__(self, subject_name: Optional[Any] = ..., extensions: Any = ...) -> None: ...
    def subject_name(self, name: Any): ...
    def add_extension(self, extension: Any, critical: Any): ...
    def sign(self, private_key: Any, algorithm: Any, backend: Any): ...

class CertificateBuilder:
    def __init__(self, issuer_name: Optional[Any] = ..., subject_name: Optional[Any] = ..., public_key: Optional[Any] = ..., serial_number: Optional[Any] = ..., not_valid_before: Optional[Any] = ..., not_valid_after: Optional[Any] = ..., extensions: Any = ...) -> None: ...
    def issuer_name(self, name: Any): ...
    def subject_name(self, name: Any): ...
    def public_key(self, key: Any): ...
    def serial_number(self, number: Any): ...
    def not_valid_before(self, time: Any): ...
    def not_valid_after(self, time: Any): ...
    def add_extension(self, extension: Any, critical: Any): ...
    def sign(self, private_key: Any, algorithm: Any, backend: Any): ...

class CertificateRevocationListBuilder:
    def __init__(self, issuer_name: Optional[Any] = ..., last_update: Optional[Any] = ..., next_update: Optional[Any] = ..., extensions: Any = ..., revoked_certificates: Any = ...) -> None: ...
    def issuer_name(self, issuer_name: Any): ...
    def last_update(self, last_update: Any): ...
    def next_update(self, next_update: Any): ...
    def add_extension(self, extension: Any, critical: Any): ...
    def add_revoked_certificate(self, revoked_certificate: Any): ...
    def sign(self, private_key: Any, algorithm: Any, backend: Any): ...

class RevokedCertificateBuilder:
    def __init__(self, serial_number: Optional[Any] = ..., revocation_date: Optional[Any] = ..., extensions: Any = ...) -> None: ...
    def serial_number(self, number: Any): ...
    def revocation_date(self, time: Any): ...
    def add_extension(self, extension: Any, critical: Any): ...
    def build(self, backend: Any): ...

def random_serial_number(): ...