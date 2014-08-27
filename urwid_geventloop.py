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
from gevent.event import AsyncResult


__version__ = '0.0.0.dev'
__all__ = ['GeventLoop']


class GeventLoop(object):

    def __init__(self):
        super(GeventLoop, self).__init__()
        self._greenlets = set()
        self._idle_handle = 0
        self._idle_callbacks = {}
        self._exit = AsyncResult()

    def _greenlet_spawned(self, greenlet):
        greenlet.link(self._greenlet_callback)
        greenlet.link_exception(self._greenlet_failed)
        self._greenlets.add(greenlet)
        return greenlet

    def _greenlet_callback(self, greenlet):
        self._greenlets.discard(greenlet)
        self._entering_idle()

    def _greenlet_failed(self, greenlet):
        self._exit.set_exception(greenlet.exception)

    # alarm

    def alarm(self, seconds, callback):
        greenlet = gevent.spawn_later(seconds, callback)
        return self._greenlet_spawned(greenlet)

    def remove_alarm(self, handle):
        if handle._start_event.active:
            handle._start_event.stop()
            return True
        return False

    # file

    def _watch_file(self, fd, callback):
        while True:
            select.select([fd], [], [])
            self._greenlet_spawned(gevent.spawn(callback))

    def watch_file(self, fd, callback):
        greenlet = gevent.spawn(self._watch_file, fd, callback)
        return self._greenlet_spawned(greenlet)

    def remove_watch_file(self, handle):
        handle.kill()
        return True

    # idle

    def _entering_idle(self):
        for callback in self._idle_callbacks.values():
            callback()

    def enter_idle(self, callback):
        self._idle_handle += 1
        self._idle_callbacks[self._idle_handle] = callback
        return self._idle_handle

    def remove_enter_idle(self, handle):
        try:
            del self._idle_callbacks[handle]
        except KeyError:
            return False
        return True

    def run(self):
        while True:
            greenlets = [self._exit]
            greenlets.extend(self._greenlets)
            try:
                gevent.joinall(greenlets, timeout=1, raise_error=True)
            except gevent.Timeout:
                pass
            self._entering_idle()
