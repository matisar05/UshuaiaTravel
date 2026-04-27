import os
import threading
from django.apps import AppConfig
from django.core.management import call_command


class HotelsConfig(AppConfig):
    name = 'hotels'

    def ready(self):
        # Prevent running twice when using Django's auto-reloader
        if os.environ.get('RUN_MAIN') == 'true':
            def run_scraper():
                print("Starting initial scrape in background...")
                try:
                    call_command('scrape_hotels', platform='booking', max_hotels=10)
                except Exception as e:
                    print(f"Error running initial scrape: {e}")

            # Run in a separate thread to not block startup
            thread = threading.Thread(target=run_scraper)
            thread.daemon = True
            thread.start()
