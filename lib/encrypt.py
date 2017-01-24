from base64 import b64decode, b64encode
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA
from exceptions import *

BS = 16

# Remember to change them for every client!
CLIENT_PRIV_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAsyP0rCgIivGiMZbLxriIOQXkHxydG9R3wQvwXkZYBgDLOrBk
3smyN6lI0eK0LoiK4wAuZctu+Q3xIV+iYEQj/Ms1LyIOLmmKlQyCj/uSSUenTTjS
Mv9FDcDWpwI+xZrdU4TtjfXxCZ9QHc3qnjQ3o30QdUbWH2r2UuR9EtarrB52kgWW
sLOjBmerUcT97zaY/b/ePks/itfovjfBmri6/LjCmo03CQ1RVxJvUD6MrNOpAhyW
Hs62DHhAqQMv1NNkLRrmkR1tcCk7BN/Z09vvue0wiO8iZAbjHOfzBtbXLFO8h3lF
cK+YXKc2l2DvmLVL6rcJPNdipMObhwWP/4swZQIDAQABAoIBAQChtwG3L+SWWY+L
qI+Icyk2IOVQWKpTZzg8IyT4VhQ8RxcvgfFtVTL3IHDGWBtELqsCRTWdW0pwtm9J
K2YP9TNvj5oRVHLs3wXli4eJpxbl5DNZeMP4mYyi38Rmu5YjGKxYKxWwI6dWgmT2
ot77tjPL+KiU1j+R2SNIrU9jZDtRgiN23MAEzfx1XnJfSnqj8foWyFBFqoQN1Krh
o/Yw0ho9BQ62svAzBsY33oB4CmICTVgcIG0dpOGb2k0EiPblPEVTYUZ7nFtW8heM
hEouZhfrEkvP+8/e91+EAPbmcbomLVgxJjT5sWbM4d9QdvdiApCJ/YAmq2M1cZSy
ha3fkAg5AoGBAOD4fw6A5QezRbjsIZf1jeRgZQpUR8mQ3nmhQXCChxRrLDM4pG+9
4vCpDEGVh5QbprzZflKVmrpOU/d9yvBuz3t1PSdUv8yMSYpCIHwl1r7e9msRT61l
gWMdoHbZarjq7C6UgbrJnM+bYrTMXTyjxbCnksutllFAxc6Ni40Cp5TrAoGBAMvZ
PKFCiORD4UZuM8bXA3h9mczEDYJ0TpsKYMFsNSsYG5A0pjlJdNmwUHtu389YGpLk
kWGH9yxrYcmX9bmqCnmkndy+KGjf3o38Sj7eKZSU0hmEBG9UvOkoOF70ahT2FtOU
JCCl0R9kFbrtNvMs5yYiRdFzVnP3jzmt9VmEDzvvAoGAF4xrYE1FrASr66tr6Mgf
TiR47xfbW9H6N6kVfH1tPknpmoL3U2sA8kf/rG3Gf05VqbbqbiKSy6WfTGyybXBr
73RaLl/Eo9ibagl59QTQ8bHNAXAScwgI/yL+xPIFJc4RYt7QpYitDV4qetpZeBt8
ef1QdFl7Po4VJoXScbQxbnkCgYEAiqA48xFkNpdS46qd22LtIUuJBA9vgH/H1PfB
xMfpgFzsoaysPdkOddvJX6eO3Fp1998oXsMv/C0qWwXUPWa9qOuhzzQiFu/nUXd4
pjg+3qQ2HNQCkBN4RLbtXuWoHokcDNZ5mxoolMhjXrNi4wxuRSiZgk6FRGfeJsN+
TlnYYlECgYBzh+/ilDNqgz9CJk+mRPtlJYS4IJtIay+QQ6bFhne/5CcukMu0lEF4
Gt+f0ZpHyqUc42S8VFzIyc/SR+b744O/qvSrRgy6tuFOwjTfDAH8wmTX+Q0PPNbw
Nm4lyAoq5NiTv+gjSaQcMn4N8rScESlSAn/Wm4zbb8bXQZn9oG1eKw==
-----END RSA PRIVATE KEY-----
"""
CLIENT_PUB_KEY = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCzI/SsKAiK8aIxlsvGuIg5BeQfHJ0b1HfBC' \
                 '/BeRlgGAMs6sGTeybI3qUjR4rQuiIrjAC5ly275DfEhX6JgRCP8yzUvIg4uaYqVDIKP+5JJR6dNONIy' \
                 '/0UNwNanAj7Fmt1ThO2N9fEJn1AdzeqeNDejfRB1RtYfavZS5H0S1qusHnaSBZaws6MGZ6tRxP3vNpj9v94+Sz+K1+i' \
                 '+N8GauLr8uMKajTcJDVFXEm9QPoys06kCHJYezrYMeECpAy/U02QtGuaRHW1wKTsE39nT2++57TCI7yJkBuMc5' \
                 '/MG1tcsU7yHeUVwr5hcpzaXYO+YtUvqtwk812Kkw5uHBY//izBl'

SRV_PUB_KEY = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDgxgsVGsKcwTT964pSUIF5IU/uXOPJCgKg8M+wfTn8dngqr2' \
              '+qXTGstHb3t80MO5sOtO5IZCzsLhpZhIJouNcfDFsHH3f64adoCSFWfhBCm0kBTToWhS4NV8j9Caj0NA5Ax34QB/vFL8R4J' \
              '/B0x2BfBo7QIWO2HoKc+EHjTWqf6lyxEzXqCVyW03M5ofo1KNtduHmxWK9wS' \
              '/2tHVkAlLCFUJzZBZCgmCrYviTMsndigxTQ0EHSWXVeqNh5OBMza1HM2+6kOZVof7/0Ot1Rd' \
              '+orK6eBziKe1suPG2ficg6yzvz9iErnqboGGwyxNz5ofo+P+5w4agzjdYN9l2H/IJZ5'


def RSAencrypt(message):
    # First sign the message
    signature = _create_signature(message)

    key = RSA.importKey(SRV_PUB_KEY)
    cipher = PKCS1_OAEP.new(key)
    ciphertext = cipher.encrypt(message)

    return {'data': b64encode(ciphertext), 'sign': b64encode(signature)}


def RSAdecrypt(ciphertext, signature):
    ciphertext = b64decode(ciphertext)
    signature = b64decode(signature)

    key = RSA.importKey(CLIENT_PRIV_KEY)
    cipher = PKCS1_OAEP.new(key)
    message = cipher.decrypt(ciphertext)

    if not _verify_signature(message, signature):
        raise RSAFailedSignature

    return message


def AESencrypt(message, key):
    signature = _create_signature(message)

    message = _pad(message)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = iv + cipher.encrypt(message)

    return {'data': b64encode(ciphertext), 'signature': b64encode(signature)}


def AESdecrypt(ciphertext, signature, key):
    ciphertext = b64decode(ciphertext)
    signature = b64decode(signature)

    iv = ciphertext[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    message = _unpad(cipher.decrypt(ciphertext[16:]))

    if not _verify_signature(message, signature):
        raise AESFailedSignature

    return message


def _create_signature(message):
    key = RSA.importKey(CLIENT_PRIV_KEY)
    h = SHA.new()
    h.update(message)
    signer = PKCS1_PSS.new(key)

    return signer.sign(h)


def _verify_signature(message, signature):
    key = RSA.importKey(SRV_PUB_KEY)
    h = SHA.new()
    h.update(message)
    verifier = PKCS1_PSS.new(key)

    return verifier.verify(h, signature)


def _pad(s):
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)


def _unpad(s):
    return s[:-ord(s[len(s) - 1:])]

