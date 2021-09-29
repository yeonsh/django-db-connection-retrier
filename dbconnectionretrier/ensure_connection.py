import logging

from time import sleep

import aspectlib

from django.db import OperationalError
from django.conf import settings

LOGGER = logging.getLogger(__name__)

ERROR_MESSAGE = "could not translate host name"
if hasattr(settings, 'DB_CONNECTION_RETRY_STRING'):
    ERROR_MESSAGE = settings.DB_CONNECTION_RETRY_STRING
    print(ERROR_MESSAGE)


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
            if ERROR_MESSAGE not in message:
                raise
            if trial == max_tries - 1:
                raise
            sleep(2 ** trial)

            LOGGER.warning(
                "Database connection lost, retrying trial %d: %s",
                trial,
                message,
            )
