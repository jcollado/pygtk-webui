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
        asynchronous_gtk_message(
            self.widget.execute_script)(message)

    def receive(self, timeout=0.1):
        try:
            message = self.message_queue.get(timeout=timeout)
        except Queue.Empty:
            return None

        logging.debug('>>> %s', message)
        return message


def start_gtk_thread():
    """Start GTK in its own thread."""
    logging.debug('Starting gtk thread...')
    gtk.gdk.threads_init()
    thread = threading.Thread(target=gtk.main)
    thread.start()


def kill_gtk_thread():
    """Terminate GTK thread."""
    asynchronous_gtk_message(gtk.main_quit)()


def asynchronous_gtk_message(fun):
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


def synchronous_gtk_message(fun):
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
