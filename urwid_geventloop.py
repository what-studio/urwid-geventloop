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


__version__ = '0.0.0.dev'
__all__ = ['GeventLoop']


class GeventLoop(object):

    def __init__(self):
        super(GeventLoop, self).__init__()
        self._greenlets = []
        self._idle_callbacks = []

    def _greenlet_spawned(self, greenlet):
        greenlet.link(self._greenlet_completed)
        self._greenlets.append(greenlet)
        return greenlet

    def _greenlet_completed(self, greenlet):
        self._entering_idle()

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
        for callback in self._idle_callbacks:
            callback()

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
                completed_greenlets = []
                for greenlet in self._greenlets:
                    try:
                        greenlet.get(block=False)
                        completed_greenlets.append(greenlet)
                    except gevent.Timeout:
                        pass
                for greenlet in completed_greenlets:
                    self._greenlets.remove(greenlet)
                self._entering_idle()
                gevent.sleep(1)
        except ExitMainLoop:
            pass
