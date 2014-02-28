import json
import logging

import gobject
import webkit


class Browser(gobject.GObject):
    """Webkit browser wrapper to exchange messages with pygtk.

    :param uri: URI to the HTML file to be displayed.
    :type uri: str

    """
    __gsignals__ = {
        'message-received': (gobject.SIGNAL_RUN_FIRST, None, (object,))
    }

    def __init__(self, uri):
        # Initialize to be able to emit signals
        gobject.GObject.__init__(self)

        self.widget = webkit.WebView()
        self.widget.open(uri)
        self.widget.connect('title-changed', self.title_changed_cb)

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
        """Send message from gtk to webkit.

        :param message: javascript code to execute in the browser widget
        :type message: str

        """
        logging.debug('(gtk -> webkit) %s', message)
        self.widget.execute_script(message)

# Register to be able to emit signals
gobject.type_register(Browser)
