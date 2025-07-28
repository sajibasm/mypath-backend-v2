#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import dotenv
import os
import sys


def main():
    # Load the .env file
    dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rootApp.settings')  # Make sure this is the correct settings file
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHON PATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
