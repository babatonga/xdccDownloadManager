from django.apps import AppConfig
import sys
import logging
import signal

logger = logging.getLogger(__name__)

class IrcXdccManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'irc_xdcc_manager'

    def ready(self):
        # don't run during make migrations or migrate or createsuperuser
        if 'makemigrations' in sys.argv or 'migrate' in sys.argv or 'createsuperuser' in sys.argv:
            return
        import irc_xdcc_manager.signals
        signal.signal(signal.SIGINT, self.shutdown_clients)
        signal.signal(signal.SIGTERM, self.shutdown_clients)

    def shutdown_clients(self, signum, frame):
        """Shut down all IRC clients gracefully when a signal is received."""
        
        if hasattr(self, 'irc_clients'):
            logger.info(f"Signal {signum} received. Shutting down IRC clients.")
            for client_data in self.irc_clients:
                client = client_data['client']
                try:
                    client.stop()  # Stop the client
                    logger.info(f"Stopped IRC client for {client_data['server']}")
                except Exception as e:
                    logger.error(f"Error stopping IRC client for {client_data['server']}: {e}")

    