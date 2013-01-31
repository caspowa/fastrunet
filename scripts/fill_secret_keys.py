import os
from random import choice
import string
import sys


DEFAULT_RANDOM_KEY_LENGTH = 24

GOOGLE_SECRET_KEYS_FILE_NAME = 'google.txt'
FACEBOOK_SECRET_KEYS_FILE_NAME = 'facebook.txt'
RECAPTCHA_SECRET_KEYS_FILE_NAME = 'recaptcha.txt'
MAIL_PASSWORD_FILE_NAME = 'email.txt'


HIDDEN_SECRET_KEY = '$SECRET_KEY'
HIDDEN_CSRF_SESSION_KEY = '%$CSRF_SESSION_KEY'

HIDDEN_GOOGLE_CLIENT_ID = '$GOOGLE_CLIENT_ID'
HIDDEN_GOOGLE_CLIENT_SECRET = '$GOOGLE_CLIENT_SECRET'

HIDDEN_FACEBOOK_APP_ID = '$FACEBOOK_APP_ID'
HIDDEN_FACEBOOK_APP_SECRET = '$FACEBOOK_APP_SECRET'

HIDDEN_RECAPTCHA_PUBLIC_KEY = '$RECAPTCHA_PUBLIC_KEY'
HIDDEN_RECAPTCHA_PRIVATE_KEY = '$RECAPTCHA_PRIVATE_KEY'

HIDDEN_MAIL_PASSWORD = '$MAIL_PASSWORD'


def generate_random_key():
    chars = string.letters + string.digits
    return ''.join([choice(chars) for i in range(DEFAULT_RANDOM_KEY_LENGTH)])


def read_keys(secret_key_file_path):
    keys = []
    with open(secret_key_file_path, 'rb') as secret_key_file:
        for line in secret_key_file.readlines():
            if not line.strip() or line.startswith('#'):
                continue
            keys.append(line.split()[-1])
    return keys


def update_site_keys(template):
    secret_key = generate_random_key()
    csef_session_key = generate_random_key()
    return template.replace(HIDDEN_SECRET_KEY, secret_key).\
    replace(HIDDEN_CSRF_SESSION_KEY, csef_session_key)


def update_google_keys(template, secret_keys_folder):
    try:
        secret_key_file_path = os.path.join(secret_keys_folder,
                                            GOOGLE_SECRET_KEYS_FILE_NAME)
        google_client_id, google_client_secret = read_keys(
            secret_key_file_path)
        return template.replace(HIDDEN_GOOGLE_CLIENT_ID, google_client_id).\
        replace(HIDDEN_GOOGLE_CLIENT_SECRET, google_client_secret)
    except:
        return template


def update_facebook_keys(template, secret_keys_folder):
    try:
        secret_key_file_path = os.path.join(secret_keys_folder,
                                            FACEBOOK_SECRET_KEYS_FILE_NAME)
        facebook_app_id, facebook_app_secret = read_keys(secret_key_file_path)
        return template.replace(HIDDEN_FACEBOOK_APP_ID, facebook_app_id).\
        replace(HIDDEN_FACEBOOK_APP_SECRET, facebook_app_secret)
    except:
        return template


def update_recaptcha_keys(template, secret_keys_folder):
    try:
        secret_key_file_path = os.path.join(secret_keys_folder,
                                            RECAPTCHA_SECRET_KEYS_FILE_NAME)
        recaptcha_public_key, recaptcha_private_key = read_keys(
            secret_key_file_path)
        return template.replace(HIDDEN_RECAPTCHA_PUBLIC_KEY,
                                recaptcha_public_key).\
        replace(HIDDEN_RECAPTCHA_PRIVATE_KEY, recaptcha_private_key)
    except:
        return template


def update_mail_password(template, secret_keys_folder):
    try:
        secret_key_file_path = os.path.join(secret_keys_folder,
                                            MAIL_PASSWORD_FILE_NAME)
        mail_password, = read_keys(secret_key_file_path)
        return template.replace(HIDDEN_MAIL_PASSWORD, mail_password)
    except:
        return template


def main(secret_keys_file_path, secret_keys_folder):
    template = ''
    print os.path.abspath(secret_keys_file_path)
    with open(secret_keys_file_path, 'rb') as secret_keys_file_template:
        template = secret_keys_file_template.read()

    template = update_site_keys(template)
    template = update_google_keys(template, secret_keys_folder)
    template = update_facebook_keys(template, secret_keys_folder)
    template = update_recaptcha_keys(template, secret_keys_folder)
    template = update_mail_password(template, secret_keys_folder)

    with open(secret_keys_file_path, 'wb') as secret_keys_file:
        secret_keys_file.write(template)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
