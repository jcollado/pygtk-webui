# pygtk-webui

## Introduction

This is an example to check the interaction between a pygtk and webkit. The
webkit side displays a bar graph with random values generated with d3.js and
the pygtk part displays a treeview with those values.


## Functionality

The functionality provided by this example is as follows:

- Random data button: when the random button is clicked a new data set is
  generated.
- Bar selection: a bar can be selected either by clicking on the tree view
  checkbox or in the graph (both the bar and label will work). The result is
  that the color of the bar changes.
- Date filtering: the to/from combo boxes can be used to select only a subset
  of the original range to be displayed in the bar graph.
- Redraw on resize: when the gtk window is resized, the graph is drawn again to
  adjust to the new size.


## Original example

The example is based on the "HOWTO Create Python GUIs using HTML" article that
can be found here:
http://www.aclevername.com/articles/python-webgui/

The main difference with the article is that there's no need to handle the
communication between pygtk and webkit in a separate thread using a queue. This
is because the trick used in the article to pass messages from webkit to pygtk
(update the page title) already handles the information within the gtk thread.

To make this communication between pygtk and webkit a little bit more elegant,
what this example provides is a `Browser` class that wraps the webkit widget
and defines a new `message-received` event that is used to let the pygtk
application know that a message has been received from webkit.
