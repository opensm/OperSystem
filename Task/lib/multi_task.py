# 多线程任务处理
# 采用信号量限制线程数,是解决高IO并发
#

from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from Task.lib.settings import *


class MultiSubTask:
    pool = None
    lock = threading.Lock()
    _templates = None

    def get_imported_class(self):
        """
        :params: return
        """
        import sys, \
            inspect
        self._templates = [
            x.startswith('Template') for x in
            inspect.getmembers(sys.modules[__name__], inspect.isclass)
        ]
        if len(self._templates):
            raise ValueError("没有导入Template")

    def run_bonded_threads(self, sub_tasks: list, run_function, max_threads=None):

        thread_list = list()
        if not max_threads:
            self.pool = ThreadPoolExecutor()
        else:
            self.pool = ThreadPoolExecutor(max_workers=max_threads)
        for x in self.split_subtask(
                all_sub_tasks=sub_tasks,
                max_thread=max_threads
        ):
            with self.pool as th:
                t_sub = th.submit(run_function, args=(x,))
                thread_list.append(t_sub)
        # 逐步校验执行结果
        for t in as_completed(thread_list):
            if not t.result():
                return False
        return True

    @staticmethod
    def split_subtask(all_sub_tasks: list, max_thread=None):
        """分配任务列表到各个线程"""
        import os
        sub_tasks = []
        if max_thread is None:
            # ThreadPoolExecutor is often used to:
            # * CPU bound task which releases GIL
            # * I/O bound task (which releases GIL, of course)
            #
            # We use cpu_count + 4 for both types of tasks.
            # But we limit it to 32 to avoid consuming surprisingly large resource
            # on many core machine.
            max_thread = min(32, (os.cpu_count() or 1) + 4)
        if max_thread <= 0:
            raise ValueError("max_workers must be greater than 0")
        if len(all_sub_tasks) > max_thread:
            for x in range(0, len(all_sub_tasks), max_thread):
                sub_tasks.append(all_sub_tasks[x:x + max_thread])
        elif 0 < len(all_sub_tasks) < max_thread:
            for x in range(0, len(all_sub_tasks)):
                sub_tasks.append([all_sub_tasks[x]])
        else:
            raise ValueError("all_sub_tasks must be greater than 0")
        return sub_tasks

    def lock_thread(self):
        self.lock.acquire()

    def unlock_thread(self):
        self.lock.release()

    def __del__(self):
        pass
