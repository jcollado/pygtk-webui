#!/usr/bin/env python

import json
import logging
import operator
import os
import random
import signal
import urllib.request

from gi.repository import Gtk
from functools import wraps

from uifile import UIFile
from browser import Browser


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
    def __init__(self):
        UIFile.__init__(self, 'demo.ui')

        # glade should take care of this relationship,
        # but I haven't found how to do it
        self.window.add_accel_group(self.accel_group)

        # Create a proper file:// URL pointing to index.html:
        fname = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'html',
            'index.html')

        uri = 'file://' + urllib.request.pathname2url(fname)
        self.browser = Browser(uri)
        self.browser_box.pack_start(
            self.browser.widget, expand=True, fill=True, padding=0)
        self.browser.connect(
            'message-received', self.browser_message_received_cb)

    @trace
    def main(self):
        """Main method used to display the application UI."""
        self.window.show_all()
        Gtk.main()

    @trace
    def browser_message_received_cb(self, browser, message):
        """Handle message send by webbrowser.

        :param browser: Browser object that sent the message
        :type browser: webgui.Browser
        :param message: Message containing event data
        :type message: dict

        """
        logging.debug('(webkit -> Gtk) %s', message)
        assert isinstance(message, dict)
        event = message['event']
        if event == 'document-ready':
            self.random_data_btn.emit('clicked')
        elif event == 'bar-clicked' or event == 'label-clicked':
            self.selected_renderer.emit('toggled', message['index'])
        else:
            raise ValueError('Unknown browser message: {}'.format(message))

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
    def update_graph(self):
        """Update graph in the webkit widget."""
        dataset = [
            {'date': r[0],
             'value': r[1],
             'selected': r[2],
             }
            for r in self.data_store]

        from_month = self.from_combobox.get_active()
        to_month = self.to_combobox.get_active() + 1

        self.browser.send(
            'draw({})'.format(json.dumps(dataset[from_month:to_month])))

    @trace
    def random_data_btn_clicked_cb(self, _button):
        """Send new random dataset to browser."""
        dataset = self.gen_random_dataset()
        self.browser.send('draw({})'.format(json.dumps(dataset)))

    @trace
    def selected_renderer_toggled_cb(self, renderer, path):
        """Update model to check/uncheck row.

        :param renderer: Renderer object that emitted the toggled event
        :type renderer: Gtk.CellRendererToggle
        :param path: Path to the row that has been toggled
        :type path: int

        """
        logging.debug('selected renderer toggled: path: %s', path)
        row = self.data_store[path]
        row[2] = not row[2]

        self.update_graph()

    @trace
    def value_renderer_edited_cb(self, renderer, path, new_text):
        logging.debug('value renderer edited: path: %s, new_text: %s',
                      path, new_text)

        try:
            new_value = int(new_text)
        except ValueError:
            logging.error("new_text isn' an integer: %s", new_text)
            return

        row = self.data_store[path]
        row[1] = new_value
        self.update_graph()

    @trace
    def from_combobox_changed_cb(self, combobox):
        logging.debug('from combobox changed: %s', combobox.get_active())
        self.update_graph()

    @trace
    def to_combobox_changed_cb(self, combobox):
        logging.debug('to combobox changed: %s', combobox.get_active())
        self.update_graph()

    @trace
    def quit_activate_cb(self, _menuitem):
        """Quit application when quit menu item is activated."""
        Gtk.main_quit()

    def window_check_resize_cb(self, _window):
        """Redraw graph after window resize."""
        # A vertical border is needed
        # to prevent the browser widget from resizing on every event
        v_border = 20

        width, height = self.browser.size
        if width > 0 and height > v_border:
            self.browser.send(
                'resize({}, {})'.format(width, height - v_border))

    @trace
    def window_destroy_cb(self, _window):
        """Quit application when main window is destroyed."""
        Gtk.main_quit()


def main():
    """Launch application."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s: %(message)s')

    @trace
    def sigint_handler(*args):
        """Exit on Ctrl+C"""
        Gtk.main_quit()

    signal.signal(signal.SIGINT, sigint_handler)

    application = Application()
    application.main()

if __name__ == '__main__':
    main()
