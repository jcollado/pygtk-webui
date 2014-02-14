#!/usr/bin/python
import logging
import os
import signal
import threading
import time
import urllib

from functools import wraps

from uifile import UIFile

from webgui import (
    Browser,
    GtkThread,
    )


def trace(func):
    """Tracing wrapper to log when function enter/exit happens."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug('Start {!r}'. format(func.__name__))
        result = func(*args, **kwargs)
        logging.debug('End {!r}'. format(func.__name__))
        return result
    return wrapper


class Application(UIFile):
    def __init__(self, quit):
        UIFile.__init__(self, 'demo.ui')

        self.quit = quit

        # glade should take care of this relationship,
        # but I haven't found how to do it
        self.window.add_accel_group(self.accel_group)

        # Create a proper file:// URL pointing to demo.html:
        fname = os.path.abspath('demo.html')
        uri = 'file://' + urllib.pathname2url(fname)
        self.browser = Browser(uri)
        self.vbox.pack_start(
            self.browser.widget, expand=True, fill=True, padding=0)

    @GtkThread.asynchronous_message
    @trace
    def main(self):
        self.window.show_all()

    @trace
    def quit_activate_cb(self, args):
        self.quit.set()

    @trace
    def window_destroy_cb(self, args):
        self.quit.set()


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s: %(message)s')

    quit = threading.Event()

    @trace
    def sigint_handler(*args):
        """Exit on Ctrl+C"""
        quit.set()

    signal.signal(signal.SIGINT, sigint_handler)

    application = GtkThread.synchronous_message(Application)(quit)
    application.main()
    browser = application.browser

    # Finally, here is our personalized main loop, 100% friendly
    # with "select" (although I am not using select here)!:
    last_second = time.time()
    uptime_seconds = 1
    clicks = 0
    while not quit.is_set():
        current_time = time.time()
        message = browser.receive()

        if message == 'clicked':
            clicks += 1
            browser.send('$messages.text("{} clicks so far")'.format(clicks))

        if current_time - last_second >= 1.0:
            browser.send('$uptime_value.text("{}")'.format(uptime_seconds))
            uptime_seconds += 1
            last_second += 1.0


if __name__ == '__main__':
    with GtkThread():
        main()
