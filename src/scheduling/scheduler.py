import logging
import sched
import threading
import time
from datetime import timedelta

from utils import date_utils

_sleep = time.sleep

LOGGER = logging.getLogger('script_server.scheduling.scheduler')


class Scheduler:
    def __init__(self) -> None:
        self.stopped = False
        self._events = {}  # Maps job_path to scheduler event

        self.scheduler = sched.scheduler(timefunc=time.time)
        self._start_scheduler()

    def _start_scheduler(self):
        def scheduler_loop():
            while not self.stopped:
                try:
                    self.scheduler.run(blocking=False)
                except Exception as e:
                    LOGGER.exception('Failed to execute scheduled job: %s', e)

                now = date_utils.now()
                sleep_delta = timedelta(seconds=1) - timedelta(microseconds=now.microsecond)
                _sleep(sleep_delta.total_seconds())

        self.scheduling_thread = threading.Thread(daemon=True, target=scheduler_loop)
        self.scheduling_thread.start()

    def stop(self):
        self.stopped = True

        def stopper():
            pass

        # just schedule the next execution to exit thread immediately
        self.scheduler.enter(1, 0, stopper)

        self.scheduling_thread.join(1)

    def schedule(self, execute_at_datetime, callback, params):
        # params[1] is job_path in the schedule_service usage
        job_path = params[1] if len(params) > 1 else None
        event = self.scheduler.enterabs(execute_at_datetime.timestamp(), 1, callback, params)
        if job_path:
            self._events[job_path] = event

    def cancel(self, job_path):
        """Cancel a scheduled job by its job_path"""
        if job_path in self._events:
            try:
                self.scheduler.cancel(self._events[job_path])
                del self._events[job_path]
                LOGGER.info(f'Cancelled scheduled job: {job_path}')
            except ValueError:
                # Event already executed or not in queue
                del self._events[job_path]
                LOGGER.debug(f'Job {job_path} was not in scheduler queue (may have already executed)')
