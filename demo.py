#!/usr/bin/python
import json
import logging
import operator
import os
import random
import signal
import threading
import urllib

from functools import wraps

from uifile import UIFile

from webgui import (
    Browser,
    GtkThread,
    )


def trace(func):
    """Tracing wrapper to log when function enter/exit happens.

    :param func: Function to wrap
    :type func: callable

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug('Start {!r}'. format(func.__name__))
        result = func(*args, **kwargs)
        logging.debug('End {!r}'. format(func.__name__))
        return result
    return wrapper


class Application(UIFile):
    """Gtk application."""
    def __init__(self, quit):
        UIFile.__init__(self, 'demo.ui')

        self.quit = quit

        # glade should take care of this relationship,
        # but I haven't found how to do it
        self.window.add_accel_group(self.accel_group)

        # Create a proper file:// URL pointing to index.html:
        fname = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'html',
            'index.html')
        uri = 'file://' + urllib.pathname2url(fname)
        self.browser = Browser(uri)
        self.browser_box.pack_start(
            self.browser.widget, expand=True, fill=True, padding=0)

    @GtkThread.asynchronous_message
    @trace
    def main(self):
        """Main method used to display the application UI."""
        self.window.show_all()

    @trace
    def gen_random_dataset(self):
        """Generate random data for the demo."""
        year = 2013
        month_count = 12
        min_value = 1
        max_value = 20

        dataset = [
            {'date': '{}-{:02d}'.format(year, month),
             'value': random.randint(min_value, max_value),
             'selected': False,
             }
            for month in range(1, month_count + 1)
        ]

        # Sync random data with data_store
        self.data_store.clear()
        data_to_tuple = operator.itemgetter('date', 'value', 'selected')
        for data in dataset:
            self.data_store.append(
                data_to_tuple(data))

        return dataset

    @trace
    def random_data_btn_clicked_cb(self, _button):
        """Send new random dataset to browser."""
        dataset = self.gen_random_dataset()
        self.browser.send('draw({})'.format(json.dumps(dataset)))

    @trace
    def data_treeview_cursor_changed_cb(self, treeview):
        path, column = treeview.get_cursor()

        if column is self.selected_column:
            row = self.data_store[path]
            row[2] = not row[2]

            dataset = [
                {'date': r[0],
                 'value': r[1],
                 'selected': r[2],
                 }
                for r in self.data_store]
            self.browser.send('draw({})'.format(json.dumps(dataset)))

    @trace
    def quit_activate_cb(self, _menuitem):
        """Quit application when quit menu item is activated."""
        self.quit.set()

    @trace
    def window_destroy_cb(self, _window):
        """Quit application when main window is destroyed."""
        self.quit.set()


def main():
    """Launch application."""
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

    # Custom main loop to communicate gtk and webkit
    # Note: There must be some timeout in the loop to give a chance to the
    # signal handler to execute. Otherwise, if the main thread is blocked
    # waiting for a message in a queue, then it might now handle timely the
    # SIGINT signal.
    while not quit.is_set():
        message = browser.receive(timeout=1)
        if message == "document-ready":
            application.random_data_btn.emit('clicked')

if __name__ == '__main__':
    with GtkThread():
        main()
