import logging
import Queue
import threading

import gtk
import gobject

import webkit


class Browser(object):
    """Webkit browser wrapper to exchange messages with pygtk."""
    def __init__(self, uri):
        self.widget = webkit.WebView()
        self.widget.open(uri)
        self.message_queue = Queue.Queue()
        self.widget.connect('title-changed', self.title_changed)

    def title_changed(self, _widget, _frame, title):
        if title != 'null':
            self.message_queue.put(title)

    def send(self, message):
        logging.debug('<<< %s', message)
        GtkThread.asynchronous_message(
            self.widget.execute_script)(message)

    def receive(self, timeout=0.1):
        try:
            message = self.message_queue.get(timeout=timeout)
        except Queue.Empty:
            return None

        logging.debug('>>> %s', message)
        return message


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
