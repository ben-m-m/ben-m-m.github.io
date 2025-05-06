# generate_keys.py
import rsa

(public_key, private_key) = rsa.newkeys(2048)

with open("public.pem", "wb") as pub_file:
    pub_file.write(public_key.save_pkcs1("PEM"))

with open("private.pem", "wb") as priv_file:
    priv_file.write(private_key.save_pkcs1("PEM"))

print("✅ RSA keys generated: public.pem and private.pem")
