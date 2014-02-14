"""
User interface file handling classes
"""
import os

from collections import defaultdict

import gtk


class UIFile(object):
    """
    Load user interface file and provide the following features:

    * Connect callbacks methods from ui file
    * Attribute access to widgets in the ui file through
      ``Gtk.Builder.get_object()``
    * Helper methods to connect/disconnect all signal handlers to
      other objects. This is useful for dialogs that are destroyed,
      but connect to signals of other objects that remain alive. This
      is important because otherwise a reference to the callback
      methods is kept and, in fact, those callbacks are executed even
      after the dialog has been destroyed.
    """
    def __init__(self, ui_filename):
        """
        Open user interface file and connect widgets to callback methods

        :param ui_filename: Name pointing to the user interface file
        :type ui_filename: str
        :returns: None
        """
        # It's assumed that ui_filename is located
        # under 'ui' directory relative to source file path
        ui_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'ui', ui_filename)

        builder = gtk.Builder()
        builder.add_from_file(ui_filename)
        builder.connect_signals(self)
        object.__setattr__(self, 'builder', builder)

        # Keep a record of all handlers to disconnect them later if needed
        self._handler_ids = defaultdict(list)

    def __getattr__(self, name):
        """
        Look for widgets in builder object as attributes

        :param name: Attribute name
        :type name: str
        :returns: Widget
        :rtype: ``Gtk.Widget`` (any of its subclasses)
        :raises: ``AtributeError`` when the attribute definition
         is not found in the ui file
        """
        obj = self.builder.get_object(name)

        if obj is None:
            raise AttributeError(name)

        return obj

    def connect(self, obj, signal, handler, *args):
        """
        Connect signal handler and keep a record of its id
        to disconnect it on destroy

        :param obj: Object that will emit the signal
        :type obj: ``gobject.GObject``
        :param signal: Signal name
        :type signal: str
        :param handler: Callback to be executed when the signal is emitted
        :type handler: function | bound method
        :param args: Additional arguments required by the signal
        :type args: iterable
        :returns: None
        """
        handler_id = obj.connect(signal, handler, *args)
        self._handler_ids[obj].append(handler_id)

    def disconnect_all(self):
        """
        Disconnect all handlers

        :returns: None
        """
        for obj, handler_ids in self._handler_ids.iteritems():
            for handler_id in handler_ids:
                if obj.handler_is_connected(handler_id):
                    obj.disconnect(handler_id)
