# -*- coding: utf-8 -*-
"""
    urwid_geventloop
    ~~~~~~~~~~~~~~~~

    Event loop based on gevent.

    ::

       main_loop = urwid.MainLoop(widget, event_loop=GeventLoop())
       gevent.spawn(background_loop)
       main_loop.run()

"""
import gevent
from gevent import select
from urwid import ExitMainLoop
from collections import deque


__version__ = '0.0.0.dev'
__all__ = ['GeventLoop']


class GeventLoop(object):

    def __init__(self):
        super(GeventLoop, self).__init__()
        self._completed_greenlets = deque()
        self._idle_callbacks = []
        self._idle_event = gevent.event.Event()

    def _greenlet_completed(self, greenlet):
        self._completed_greenlets.append(greenlet)
        self._idle_event.set()

    # alarm

    def alarm(self, seconds, callback):
        greenlet = gevent.spawn_later(seconds, callback)
        greenlet.link(self._greenlet_completed)
        return greenlet

    def remove_alarm(self, handle):
        if handle._start_event.active:
            handle._start_event.stop()
            return True
        return False

    # file

    def _watch_file(self, fd, callback):
        while True:
            select.select([fd], [], [])
            gevent.spawn(callback).link(self._greenlet_completed)

    def watch_file(self, fd, callback):
        greenlet = gevent.spawn(self._watch_file, fd, callback)
        greenlet.link(self._greenlet_completed)
        return greenlet

    def remove_watch_file(self, handle):
        handle.kill()
        return True

    # idle

    def enter_idle(self, callback):
        self._idle_callbacks.append(callback)
        return callback

    def remove_enter_idle(self, handle):
        try:
            self._idle_callbacks.remove(handle)
        except KeyError:
            return False
        return True

    def run(self):
        try:
            while True:
                for callback in self._idle_callbacks:
                    callback()
                while len(self._completed_greenlets) > 0:
                    self._completed_greenlets.popleft().get(block=False)
                if self._idle_event.wait(timeout=1):
                    self._idle_event.clear()
        except ExitMainLoop:
            pass
