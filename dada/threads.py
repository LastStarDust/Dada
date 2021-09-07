#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2021 AXELSPACE
import logging
import threading
from abc import ABC, abstractmethod


class ResumableThread(threading.Thread, ABC):
    """Thread class with a pause() and resume() methods. The thread itself has to check
    regularly for the paused condition."""

    def __init__(self, *args, **kwargs):
        super(ResumableThread, self).__init__(*args, **kwargs)
        self.iterations = 0
        self.daemon = True  # Allow main to exit even if still running.
        self.paused = True  # Start out paused.
        self.state = threading.Condition()

    def pause(self):
        """
        When the pause method is called the state is set to paused. The next time the thread checks the state,
        the thread is paused. This means that there is a lag from the moment the pause method is called
        until the thread is effectively paused.
        :return: None
        """
        with self.state:
            self.paused = True  # Block self.

    def resume(self):
        """
        When the resume method is called the state is set to resumed. The next time the thread checks the state,
        the thread is resumed. This means that there is a lag from the moment the resume method is called
        until the thread is effectively resumed.
        :return: None
        """
        with self.state:
            self.paused = False
            self.state.notify()  # Unblock self if waiting.

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
        logging.debug(f"Stopping thread {id(self)}")
        self._stop_event.set()

    def is_stopped(self) -> bool:
        """
        Check if the stop flag is set
        :return: stop flag
        """
        return self._stop_event.is_set()
