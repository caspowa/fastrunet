from app import create_app


def main():
    app = create_app()
    app.run('0.0.0.0', 8080, app.config['DEBUG'])


if __name__ == '__main__':
    main()
