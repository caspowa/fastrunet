from random import choice
import string
import sys


DEFAULT_RANDOM_KEY_LENGTH = 24

HIDDEN_SECRET_KEY = '$SECRET_KEY'
HIDDEN_CSRF_SESSION_KEY = '%$CSRF_SESSION_KEY'


def generate_random_key():
    chars = string.letters + string.digits
    return ''.join([choice(chars) for i in range(DEFAULT_RANDOM_KEY_LENGTH)])


def update_site_keys(template):
    secret_key = generate_random_key()
    csef_session_key = generate_random_key()
    return template.replace(HIDDEN_SECRET_KEY, secret_key).\
        replace(HIDDEN_CSRF_SESSION_KEY, csef_session_key)


def main(secret_keys_file_path):
    with open(secret_keys_file_path, 'rb') as secret_keys_file_template:
        template = secret_keys_file_template.read()

    template = update_site_keys(template)

    with open(secret_keys_file_path, 'wb') as secret_keys_file:
        secret_keys_file.write(template)


if __name__ == '__main__':
    main(sys.argv[1])
