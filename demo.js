$(document).ready(function() {
  send('"document-ready"');
  $("#messages").on("click", function() {
    send('"got-a-click"');
  });

  var $messages = $("#messages");
});
