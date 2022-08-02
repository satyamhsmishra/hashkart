"""Application configuration."""
import os
from pathlib import Path

class LocalConfig:
    db_type = os.getenv('DB_TYPE', 'mysql')
    user = os.getenv('DB_USER', 'root')
    passwd = os.getenv('DB_PASSWD', '123456')
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = os.getenv('DB_PORT', 3306)
    db_name = os.getenv('DB_NAME', 'hashkart')
    if db_type == 'postgresql':
        db_uri = 'postgresql://{user}:{passwd}@{host}:{port}/{db_name}'.format(
            user=user, passwd=passwd, host=host, port=port, db_name=db_name)
    elif db_type == u'mysql':
        db_uri = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8mb4".format(
            user=user,passwd=passwd, host=host, port=port, db_name=db_name)
    esearch_uri = "localhost"