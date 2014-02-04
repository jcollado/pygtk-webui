#!/usr/bin/python
import os
import signal
import time
import urllib

from webgui import (
    start_gtk_thread,
    launch_browser,
    synchronous_gtk_message,
    kill_gtk_thread,
    )


class Global(object):
    quit = False

    @classmethod
    def set_quit(cls, *args, **kwargs):
        cls.quit = True


def main():
    start_gtk_thread()

    # Create a proper file:// URL pointing to demo.html:
    fname = os.path.abspath('demo.html')
    uri = 'file://' + urllib.pathname2url(fname)
    browser, web_recv, web_send = \
        synchronous_gtk_message(launch_browser)(uri,
                                                quit_function=Global.set_quit)

    # Finally, here is our personalized main loop, 100% friendly
    # with "select" (although I am not using select here)!:
    last_second = time.time()
    uptime_seconds = 1
    clicks = 0
    while not Global.quit:

        current_time = time.time()
        again = False
        msg = web_recv()
        if msg:
            again = True

        if msg == "got-a-click":
            clicks += 1
            web_send('$messages.text("{} clicks so far")'.format(clicks))

        if current_time - last_second >= 1.0:
            web_send('$uptime_value.text("{}")'.format(uptime_seconds))
            uptime_seconds += 1
            last_second += 1.0

        if again:
            pass
        else:
            time.sleep(0.1)


def my_quit_wrapper(fun):
    signal.signal(signal.SIGINT, Global.set_quit)

    def fun2(*args, **kwargs):
        try:
            x = fun(*args, **kwargs)  # equivalent to "apply"
        finally:
            kill_gtk_thread()
            Global.set_quit()
        return x
    return fun2


if __name__ == '__main__':  # <-- this line is optional
    my_quit_wrapper(main)()
