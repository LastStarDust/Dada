#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2021 AXELSPACE

import threading
from abc import ABC, abstractmethod


class ResumableThread(threading.Thread, ABC):
    """Thread class with a pause() and resume() methods. The thread itself has to check
    regularly for the paused condition."""

    def __init__(self, *args, **kwargs):
        super(ResumableThread, self).__init__(*args, **kwargs)
        self.iterations = 0
        self.daemon = False  # Do not continue blocking the device if the program crashes
        self._paused = False  # Start out unpaused
        # Explicitly using Lock over RLock since the use of self.paused
        # break reentrancy anyway, and I believe using Lock could allow
        # one thread to pause the worker, while another resumes; haven't
        # checked if Condition imposes additional limitations that would
        # prevent that. In Python 2, use of Lock instead of RLock also
        # boosts performance.
        self._pause_cond = threading.Condition(threading.Lock())

    def pause(self):
        """
        When the pause method is called the state is set to paused. The next time the thread checks the state,
        the thread is paused. This means that there is a lag from the moment the pause method is called
        until the thread is effectively paused.
        :return: None
        """
        self._paused = True
        # If in sleep, we acquire immediately, otherwise we wait for thread
        # to release condition. In race, worker will still see self.paused
        # and begin waiting until it's set back to False
        self._pause_cond.acquire()

    def resume(self):
        """
        When the resume method is called the state is set to resumed. The next time the thread checks the state,
        the thread is resumed. This means that there is a lag from the moment the resume method is called
        until the thread is effectively resumed.
        :return: None
        """
        self._paused = False
        # Notify so thread will wake after lock released
        self._pause_cond.notify()
        # Now release the lock
        self._pause_cond.release()

    @abstractmethod
    def run(self) -> None:
        pass


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self) -> None:
        """
        When the stop method is called the stop flag is set. The next time the thread checks the stop flag,
        the thread is stopped. This means that there is a lag from the moment the stop method is called
        until the thread is effectively stopped.
        :return: None
        """
        self._stop_event.set()

    def is_stopped(self) -> bool:
        """
        Check if the stop flag is set
        :return: stop flag
        """
        return self._stop_event.is_set()

    @abstractmethod
    def run(self) -> None:
        pass
