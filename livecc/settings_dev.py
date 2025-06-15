from .settings import *

# Development-specific settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
SECRET_KEY='25^l5j0a(!o6am^-$6y_tnluht0n-3z=zpemm%=&(=95o%)h6o'

#dbbackup on local host

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/Users/iqbal/Desktop/work-history/lotipoti-shop/fullzhub/dbbackup/local/'}

#remember to comment this section on production
#upload max file

DATA_UPLOAD_MAX_NUMBER_FIELDS = 104857600 # 100MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB

#It is common practice to delete the __pycache__ directories when cleaning up a project or when you want to ensure a fresh start. 

# ==========comamnd to drop migratios files=======
######## find . -name "__pycache__" -type d -exec rm -r {} +  ##########


# find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
# find . -path "*/migrations/*.pyc" -delete
# ==========comamnd to drop migratios files=======

# ==========psql comamnd to drop tables=======
# DO
# $do$
# DECLARE
#    r RECORD;
# BEGIN
#    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
#        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
#    END LOOP;

#    FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = current_schema()) LOOP
#        EXECUTE 'DROP SEQUENCE IF EXISTS ' || quote_ident(r.sequence_name) || ' CASCADE';
#    END LOOP;

#    FOR r IN (SELECT table_name FROM information_schema.views WHERE table_schema = current_schema()) LOOP
#        EXECUTE 'DROP VIEW IF EXISTS ' || quote_ident(r.table_name) || ' CASCADE';
#    END LOOP;
# END
# $do$;


# ==========psql comamnd to drop tables=======

# DELETE FROM django_migrations WHERE app='bitcoin_config';
# DROP TABLE IF EXISTS bitcoin_config_bitcoin_config;

# ==========Celery Activation=======

# celery -A livecc worker --loglevel=info
# celery -A livecc beat --loglevel=info

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',  # Use RotatingFileHandler
            'filename': 'Markcc_Warnings.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,  # Keep at most 5 log files
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

