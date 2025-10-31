from django.apps import AppConfig
import threading
import time


def _start_promos_scheduler():
    from django.core import management
    from django.core.cache import cache

    def loop():
        while True:
            try:
                # simple cache lock to avoid overlap between multiple workers (60s TTL)
                if cache.add('ensure_promos:lock', '1', timeout=50):
                    management.call_command('ensure_promos', send_email=1)
                    cache.delete('ensure_promos:lock')
            except Exception:
                # swallow errors to keep scheduler alive
                pass
            time.sleep(60)

    t = threading.Thread(target=loop, name='ensure_promos_scheduler', daemon=True)
    t.start()


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    _scheduler_started = False

    def ready(self):
        # Start the minute scheduler once per process
        if not StoreConfig._scheduler_started:
            StoreConfig._scheduler_started = True
            try:
                _start_promos_scheduler()
            except Exception:
                pass

