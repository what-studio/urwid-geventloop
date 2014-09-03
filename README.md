urwid-geventloop
================

Event loop based on gevent for urwid.

```python
 main_loop = urwid.MainLoop(widget, event_loop=GeventLoop())
 gevent.spawn(background_loop)
 main_loop.run()
 ```
 
 Install from PyPI:
 
     $ pip install urwid-geventloop
