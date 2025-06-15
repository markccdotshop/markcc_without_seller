from .settings import *

# Production-specific settings
DEBUG=False
ALLOWED_HOSTS = ['fullzhub.cc','fullzhub.cc','localhost']
SECRET_KEY='25^l5j0a(!o6am^-$6y_tnluht0n-3z=zpemm%=&(=95o%)h6o'


# ====Ensure CSRF protection is enabled====
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
# ====Secure https Settings====
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
# CSRF_TRUSTED_ORIGINS =['http://markcckimdfjg352q6on2pymzersee2rtckpsrfttaxehgbbagonplad.onion']
# Use HttpOnly cookies
# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = True
# ====Secure hsts Settings====
SECURE_HSTS_SECONDS = 15780000 #for 6 month
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Set the session to expire after a period of inactivity (e.g., 5 minutes).
SESSION_COOKIE_AGE = 3600  # 3600 seconds (60 minutes)

# Whether a user's session cookie expires when the Web browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Set to True if we want to detect when the user has become inactive (not just when the cookie expires)
SESSION_SAVE_EVERY_REQUEST = True


#dbbackup on production

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/home/fullzhub_seller_admin/backup/'}


# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
#             'style': '{',
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#         },
#     },
#     'handlers': {
#         'file': {
#             'level': 'WARNING',
#             'class': 'logging.handlers.RotatingFileHandler',  # Use RotatingFileHandler
#             'filename': 'Markcc_Warnings.log',
#             'maxBytes': 1024*1024*5,  # 5 MB
#             'backupCount': 5,  # Keep at most 5 log files
#             'formatter': 'verbose',
#         },
#     },
#     'loggers': {
#         '': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }
