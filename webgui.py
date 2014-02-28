import json
import logging
import Queue
import threading

import gtk
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
        self.message_queue = Queue.Queue()
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
        GtkThread.asynchronous_message(
            self.widget.execute_script)(message)

# Register to be able to emit signals
gobject.type_register(Browser)


class GtkThread(object):
    def start(self):
        """Start GTK in its own thread."""
        gtk.gdk.threads_init()
        self.thread = threading.Thread(target=gtk.main)
        self.thread.start()

    def kill(self):
        """Terminate GTK thread."""
        GtkThread.asynchronous_message(gtk.main_quit)()
        self.thread.join()

    def __enter__(self):
        """Start thread when entering into context manager."""
        self.start()

    def __exit__(self, _exc_type, _exc_value, _traceback):
        """Kill thread when exiting from context manager."""
        self.kill()

    @classmethod
    def asynchronous_message(cls, fun):
        """Call function in thread running gtk main loop.

        :param fun: Function to call in the thread running the gtk main loop
        :type fun: callable
        :returns: A function that wraps the original function

        """
        def worker((args, kwargs)):
            fun(*args, **kwargs)

        def fun2(*args, **kwargs):
            gobject.idle_add(worker, (args, kwargs))

        return fun2

    @classmethod
    def synchronous_message(cls, fun):
        """Call function in thread running gtk main loop and return result.

        :param fun: Function to call in the thread running the gtk main loop
        :type fun: callable
        :returns: A function that wraps the original function

        """
        condition = threading.Condition()

        def worker((result, args, kwargs)):
            with condition:
                result['result'] = fun(*args, **kwargs)
                condition.notify()

        def fun2(*args, **kwargs):
            with condition:
                result = {'result': None}
                gobject.idle_add(worker, (result, args, kwargs))
                condition.wait()
            return result['result']

        return fun2
