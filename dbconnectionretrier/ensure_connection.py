import logging

from time import sleep

import aspectlib

from django.db import OperationalError
from django.conf import settings

LOGGER = logging.getLogger(__name__)

ERROR_MESSAGES = ["could not translate host name"]
if hasattr(settings, 'DB_CONNECTION_RETRY_STRINGS'):
    ERROR_MESSAGES += settings.DB_CONNECTION_RETRY_STRINGS
    print(ERROR_MESSAGES)


@aspectlib.Aspect
def ensure_connection(instance):
    """Aspect that tries to ensure a DB connection by retrying.

    Catches name resolution errors, by filtering on OperationalError
    exceptions that contain name resolution error messages

    Useful in case the DNS resolution is shaky, as in the case
    of the Heroku environment
    """

    max_tries = 3
    for trial in range(0, max_tries):
        try:
            result = yield aspectlib.Proceed
            yield aspectlib.Return(result)
        except OperationalError as error:
            message = str(error)
            found = False
            for m in ERROR_MESSAGES:
                if m in message:
                    found = True
                    break
            if not found:
                raise
            if trial == max_tries - 1:
                raise
            sleep(2 ** trial)

            LOGGER.warning(
                "Database connection lost, retrying trial %d: %s",
                trial,
                message,
            )
