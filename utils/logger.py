# coding=utf-8
"""
    change by lu from
    create by pymu on 2020/4/29
    package: .logger.py
    project: status_document_0.1
"""
import datetime
import logging
import os
import re

from config  import setting

description = "日志信息"
LOG_PATH = setting.get_log_path()


class Logger(logging.Logger):
    """

    """

    def __init__(self, name='system', level=logging.DEBUG):
        super().__init__(name, level)
        self.level = level
        self.name = name
        self.__set_log_handler()

    def __set_log_handler(self):
        """
        日志输出格式及输出等级, 默认为INFO
        :return:
        """
        main_handler = MyLoggerHandler(filename=self.name, when='D', backup_count=5,
                                       encoding="utf-8")
        warn_handler = MyLoggerHandler(filename='警告日志', when='D',
                                       backup_count=5, encoding="utf-8")
        error_handler = MyLoggerHandler(filename='异常日志', when='D',
                                        backup_count=35, encoding="utf-8")
        debug_handler = MyLoggerHandler(filename='debug', when='D',
                                        backup_count=2, encoding="utf-8")
        # 设置日志格式
        formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        _formatter = logging.Formatter("\n%(asctime)s - %(levelname)s: %(message)s")
        debug_formatter = logging.Formatter("%(asctime)s - %(levelname)s: File %(filename)s, in %(module)s.%(funcName)s \
            \n\tFile '%(pathname)s', line %(lineno)d\n%(message)s")

        bug_filter = logging.Filter()
        bug_filter.filter = lambda record: record.levelno == logging.ERROR  # 设置过滤等级
        error_handler.addFilter(bug_filter)
        error_handler.setFormatter(_formatter)
        self.addHandler(error_handler)

        bug_filter = logging.Filter()
        bug_filter.filter = lambda record: record.levelno == logging.WARNING  # 设置过滤等级
        warn_handler.addFilter(bug_filter)
        warn_handler.setFormatter(_formatter)
        self.addHandler(warn_handler)

        bug_filter = logging.Filter()
        bug_filter.filter = lambda record: record.levelno == logging.INFO  # 设置过滤等级
        main_handler.addFilter(bug_filter)
        main_handler.setFormatter(formatter)
        self.main_handler = main_handler
        self.addHandler(main_handler)
        
        bug_filter = logging.Filter()
        bug_filter.filter = lambda record: record.levelno < logging.INFO
        debug_handler.addFilter(bug_filter)
        debug_handler.setFormatter(debug_formatter)
        self.addHandler(debug_handler)

    def reset_name(self, name):
        """
        重新设置日志文件名
        :param name:
        :return:
        """
        self.name = name
        self.removeHandler(self.main_handler)
        self.__set_log_handler()

try:
    import codecs
except ImportError:
    codecs = None


class MyLoggerHandler(logging.FileHandler):
    def __init__(self, filename, when='M', backup_count=15, encoding=None, delay=False):
        self.prefix = os.path.join(LOG_PATH, '{name}'.format(name=filename))
        self.filename = filename
        self.when = when.upper()
        # S - Every second a new file
        # M - Every minute a new file
        # H - Every hour a new file
        # D - Every day a new file
        if self.when == 'S':
            self.suffix = "%Y-%m-%d_%H-%M-%S"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.log$"
        elif self.when == 'M':
            self.suffix = "%Y-%m-%d_%H-%M"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}\.log$"
        elif self.when == 'H':
            self.suffix = "%Y-%m-%d_%H"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}\.log$"
        elif self.when == 'D':
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}$"
        else:
            raise ValueError("Invalid rollover interval specified: %s" % self.when)
        self.filePath = "%s%s.log" % (self.prefix, datetime.datetime.now().strftime(self.suffix))
        try:
            if os.path.exists(LOG_PATH) is False:
                os.makedirs(LOG_PATH)
        except Exception as e:
            print("can not make dirs")
            print("filepath is " + self.filePath)
            print(e)

        self.backupCount = backup_count
        if codecs is None:
            encoding = None
        logging.FileHandler.__init__(self, self.filePath, 'a', encoding, delay)

    def write_log(self):
        _filePath = "%s%s.log" % (self.prefix, datetime.datetime.now().strftime(self.suffix))
        if _filePath != self.filePath:
            self.filePath = _filePath
            return 1
        return 0

    def change_file(self):
        self.baseFilename = os.path.abspath(self.filePath)
        if self.stream is not None:
            self.stream.flush()
            self.stream.close()
        if not self.delay:
            self.stream = self._open()
        if self.backupCount > 0:
            for s in self.delete_old_log():
                os.remove(s)

    def delete_old_log(self):
        dir_name, base_name = os.path.split(self.baseFilename)
        file_names = os.listdir(dir_name)
        result = []
        p_len = len(self.filename)
        for fileName in file_names:
            if fileName[:p_len] == self.filename:
                suffix = fileName[p_len:]
                if re.compile(self.extMatch).match(suffix):
                    result.append(os.path.join(dir_name, fileName))
        result.sort()
        if len(result) < self.backupCount:
            result = []
        else:
            result = result[:len(result) - self.backupCount]
        return result

    def emit(self, record):
        """
        Emit a record.
        """
        # noinspection PyBroadException
        try:
            if self.write_log():
                self.change_file()
            logging.FileHandler.emit(self, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


if __name__ == "__main__":
    # to do something  
    log = Logger('info')
    import time


    for i in range(12):
        time.sleep(1)
        log.info("测试" + str(i))

