import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from scripts import population_script 

class Command(BaseCommand):
    help = 'Deletes the SQLite DB, migrates, and runs the population script'

    def handle(self, *args, **options):
        db_file = 'db.sqlite3'

        if os.path.exists(db_file):
            self.stdout.write(self.style.WARNING(f"Deleting {db_file}..."))
            os.remove(db_file)
        
        self.stdout.write("Running migrations...")
        call_command('migrate')

        self.stdout.write(self.style.SUCCESS("Populating database..."))
        
        population_script.run()

        self.stdout.write(self.style.SUCCESS("Successfully reset and repopulated the database!"))
