# Modify this Procfile to fit your needs
web: gunicorn webserver_api:app --worker-class sync --log-level DEBUG --access-logformat '%%({X-REAL-IP}i)s %%(l)s %%(u)s %%(t)s "%%(r)s" %%(s)s %%(b)s "%%(f)s" "%%(a)s"'
