"""
This script is for lauching the automation of insomniac.py
use : python automate.py --account account_name --on_duration 60 --off_duration 30
account_name must match the parameters
"""

import time
import argparse
import threading
import ctypes
import inspect

from automate import AutoInsomniac
from automate.safe_scheduler import SafeScheduler
from automate.planner import get_planning

"""
schedule.every().hour.do(job)
schedule.every().day.at("10:30").do(job)
schedule.every(5).to(10).minutes.do(job)
schedule.every().monday.do(job)
schedule.every().wednesday.at("13:15").do(job)
schedule.every().minute.at(":17").do(job)
"""


def _async_raise(tid, exctype):
    '''Raises an exception in the threads with id tid'''
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),
                                                     ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # "if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class thread_with_exception(threading.Thread):
    """
    per Answer given here
    https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread?rq=1
    """

    def _get_my_tid(self):
        """determines this (self's) thread id

        CAREFUL: this function is executed in the context of the caller
        thread, to get the identity of the thread represented by this
        instance.
        """
        if not self.is_alive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

    def raiseExc(self, exctype):
        """Raises the given exception type in the context of this thread.

        If the thread is busy in a system call (time.sleep(),
        socket.accept(), ...), the exception is simply ignored.

        If you are sure that your exception should terminate the thread,
        one way to ensure that it works is:

            t = ThreadWithExc( ... )
            ...
            t.raiseExc( SomeException )
            while t.isAlive():
                time.sleep( 0.1 )
                t.raiseExc( SomeException )

        If the exception is to be caught by the thread, you need a way to
        check that your thread has caught it.

        CAREFUL: this function is executed in the context of the
        caller thread, to raise an exception in the context of the
        thread represented by this instance.
        """
        _async_raise(self._get_my_tid(), exctype)


def run_threaded(job_func, on_duration):
    """
    function to run threaded job for a certain duration in minutes
    https://schedule.readthedocs.io/en/stable/faq.html
    """
    job_thread = thread_with_exception(target=job_func)
    job_thread.start()
    time.sleep(on_duration * 60)
    job_thread.raiseExc(KeyboardInterrupt)


def main_automation(account, on_duration, off_duration):
    start_time = "08:00"
    stop_time = "21:01"

    ai = AutoInsomniac(account)
    scheduler = SafeScheduler(reschedule_on_failure=False)
    planning = get_planning(start_time, stop_time, on_duration, off_duration)
    print(planning)
    for run_hour in planning:
        scheduler.every().day.at(run_hour).do(run_threaded, ai.use_insomniac, on_duration)

    while True:
        scheduler.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Input the parameters for automation')
    parser.add_argument('--account', type=str,
                        help='the name of the account')
    parser.add_argument('--on_duration', type=int,
                        help='the duration in minutes of the robot runs')
    parser.add_argument('--off_duration', type=int,
                        help='the duration in minutes of the robot pauses')
    args = parser.parse_args()
    account = args.account
    on_duration = args.on_duration
    off_duration = args.off_duration
    main_automation(account, on_duration, off_duration)
