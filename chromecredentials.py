import sqlite3
import os.path
import keyring
import sys
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from tabulate import tabulate

def chrome_web_credentials():
    salt = b'saltysalt'
    iv = b' ' * 16
    length = 16
    def chrome_decrypt(encrypted_value, key=None):
        # Encrypted cookies should be prefixed with 'v10' according to the
        # Chromium code. Strip it off.
        encrypted_value = encrypted_value[3:]
        # Strip padding by taking off number indicated by padding
        # eg if last is '\x0e' then ord('\x0e') == 14, so take off 14.
        # You'll need to change this function to use ord() for python2.
        def clean(x):
            return x[:len(x)-ord(x[-1])].decode('utf8')
        cipher = AES.new(key, AES.MODE_CBC, IV=iv)
        decrypted = cipher.decrypt(encrypted_value)
        return clean(decrypted)
    # If running Chrome on OSX
    if sys.platform == 'darwin':
        my_pass = keyring.get_password('Chrome Safe Storage', 'Chrome')
        my_pass = my_pass.encode('utf8')
        iterations = 1003
        cookie_file = os.path.expanduser(
            '~/Library/Application Support/Google/Chrome/Default/Login Data'
        )
    # If running Chromium on Linux
    elif sys.platform == 'linux':
        my_pass = 'peanuts'.encode('utf8')
        iterations = 1
        cookie_file = os.path.expanduser(
            '~/.config/google-chrome/Default/Login\ Data'
        )
    else:
        raise Exception("This script only works on OSX or Linux.")
    # Generate key from values above
    key = PBKDF2(my_pass, salt, length, iterations)
    conn = sqlite3.connect(cookie_file)
    sql = 'SELECT action_url, username_value, password_value FROM logins;'
    credentials_list = []
    with conn:
        for a, b, c in conn.execute(sql):
            # if there is a not encrypted value or if the encrypted value
            # doesn't start with the 'v10' prefix, return v
            if(len(c) > 0):
                decrypted_tuple = (a, b, chrome_decrypt(c, key=key))
                credentials_list.append(decrypted_tuple)
    return credentials_list

credentials = chrome_web_credentials()
print tabulate(credentials, headers=['website', 'username', 'password'])
