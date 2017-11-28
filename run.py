import os
import json
import errno
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import tornado.ioloop
import tornado.options
from tornado import httpserver

from periodic import PeriodicApplication


# server 启动方式
tornado.options.define("mode", default="api", help="", type=str)

tornado.options.define("debug", default=True, help="", type=bool)
tornado.options.define("port", default=20000, help="", type=int)
tornado.options.define("config", default="", help="", type=str)


def read_config(config_file):
    try:
        _f = open(config_file)
        _r = _f.read()
        _f.close()
        if _r is None or len(_r) == 0:
            return None
        config = json.loads(_r)
        return config
    except Exception as e:
        logging.error(e)
        return None


def init_logging(log_file):
    file_handler = TimedRotatingFileHandler(log_file, when="d", interval=1, backupCount=30)

    log_formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(lineno)d]  %(message)s"
    )
    file_handler.setFormatter(log_formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)


def init_session(config):
    if not config.get("postgres"):
        return None

    user = config.get("postgres").get("user", None)
    password = config.get("postgres").get("password", None)
    host = config.get("postgres").get("host", None)
    port = config.get("postgres").get("port", None)
    db = config.get("postgres").get("db", None)
    if not user or not password or not host or not port or not db:
        return None

    try:
        db_string = "postgresql+psycopg2://%s:%s@%s:%s/%s" % (
            user,
            password,
            host,
            port,
            db
        )
        engine = create_engine(db_string, pool_size=100)
    except Exception as e:
        logging.error(e)
        return None
    else:
        return sessionmaker(engine)


def main():
    tornado.options.parse_command_line()

    # 验证配置文件
    if tornado.options.options.config == "":
        logging.error("no config")
        return
    else:
        if not os.path.exists(tornado.options.options.config):
            logging.error("config file not exists")
            return

    # 读配置文件
    config = read_config(tornado.options.options.config)
    if not config:
        logging.error("读取配置文件失败")
        return

    # 配置文件路径
    if config.get('file', None) and \
            config.get('file').get('path', None) and \
            config.get('file').get('log', None):
        file_path = config.get('file').get('path')
        log_path = file_path + config.get('file').get('log')
    else:
        logging.error('文件系统配置错误')
        return

    # 检查是否存在目录
    if not os.path.exists(log_path):
        try:
            os.makedirs(log_path)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                logging.error(exc)
                return

    # 初始化日志系统
    init_logging("%s/QYK.%s.%s.log" % (log_path, tornado.options.options.mode, tornado.options.options.port))
    logging.info('测试日志输出')

    # 初始化数据库session 工厂
    session_class = init_session(config)
    if not session_class:
        logging.error('int session failed')
        return

    if tornado.options.options.mode == 'periodic':
        app = PeriodicApplication(session_class)
        app.run()
        logging.info("periodic server listening on port: %d" % tornado.options.options.port)

    tornado.ioloop.IOLoop.current().start()
    return


if __name__ == "__main__":
    main()
