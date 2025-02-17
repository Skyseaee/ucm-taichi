import time
import logging
import os


# 设置日志文件路径
log_dir = './file'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_file = os.path.join(log_dir, 'test_log.log')


# 配置 logging
logging.basicConfig(filename=log_file,
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s', 
                    datefmt='%m/%d/%Y %I:%M:%S %p')


def wrapper(func):
    def inner(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)

        func_name = func.__name__
        filename = kwargs.get('filename', args[0] if len(args) > 0 else 'unknown')

        end_time = time.time()
        result = end_time - start_time
        print(f'Function {func_name} time is {result}s, test file is {filename}')
        # 输出运行时间到日志文件
        logging.info('func %s time is %.6fs, test file is %s', func_name, result, filename)  
        return res

    return inner
