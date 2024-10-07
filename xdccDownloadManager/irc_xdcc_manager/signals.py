from django.db.backends.signals import connection_created
from django.db.backends.sqlite3.base import DatabaseWrapper
from django.dispatch import receiver
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

@receiver(connection_created, sender=DatabaseWrapper)
def initial_connection_to_db(sender, **kwargs):
    app_config = apps.get_app_config('irc_xdcc_manager')
    if not hasattr(app_config, 'irc_clients'):
        from .irc_agent import XDCCServerListener
        from .models import IRCConnection
        irc_clients = []
        for connection in IRCConnection.objects.filter(active=True):
            try:
                client = XDCCServerListener(connection.server)
                client.start()
                irc_clients.append({
                    'server': connection.server,
                    'client': client
                })
            except Exception as e:
                logger.error(f"Error starting IRC client for {connection.server}: {e}")
        app_config.irc_clients = irc_clients
        logger.info("IRC Clients started")