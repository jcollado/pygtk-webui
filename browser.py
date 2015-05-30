#!/usr/bin/env python

import json
import logging

from gi.repository import WebKit
from gi import _gobject as gobject


class Browser(gobject.GObject):
    """Webkit browser wrapper to exchange messages with Gtk.

    :param uri: URI to the HTML file to be displayed.
    :type uri: str

    """
    __gsignals__ = {
        'message-received': (gobject.SIGNAL_RUN_FIRST, None, (object,))
    }

    def __init__(self, uri):
        # Initialize to be able to emit signals
        gobject.GObject.__init__(self)

        self.widget = WebKit.WebView()
        self.widget.open(uri)
        self.widget.connect('title-changed', self.title_changed_cb)

    @property
    def size(self):
        """Return size of the browser widget.

        :returns: Browser widget width and height
        :rtype: tuple(int, int)

        """
        rectangle = self.widget.get_allocation()
        return (rectangle.width, rectangle.height)

    def title_changed_cb(self, _widget, _frame, title):
        """Put window title in the message queue.

        Window title changes are received as an event in the Gtk interface.
        This is used as a hack to make it possible to send messages from webkit
        to Gtk.

        :param title: Window title
        :type title: str

        """
        logging.debug('title changed: %r', title)
        message = json.loads(title)
        self.emit('message-received', message)

    def send(self, message):
        """Send message from Gtk to WebKit.

        :param message: javascript code to execute in the browser widget
        :type message: str

        """
        logging.debug('(Gtk -> WebKit) %s', message)
        self.widget.execute_script(message)

# Register to be able to emit signals
gobject.type_register(Browser)
