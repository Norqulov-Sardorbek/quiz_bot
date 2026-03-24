#!/usr/bin/env python
import os
import sys
import traceback
import asyncio


def global_exception_handler(exctype, value, tb):
    print("\n🔥 GLOBAL SYNC ERROR 🔥")
    traceback.print_exception(exctype, value, tb)


def async_exception_handler(loop, context):
    print("\n🔥 GLOBAL ASYNC ERROR 🔥")
    msg = context.get("exception", context["message"])
    print(msg)
    traceback.print_exc()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

    # 🔥 GLOBAL SYNC ERROR
    sys.excepthook = global_exception_handler

    # 🔥 GLOBAL ASYNC ERROR
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(async_exception_handler)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
