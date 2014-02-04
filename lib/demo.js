$(document).ready(function() {
  send('"document-ready"');
  $("#messages").on("click", function() {
    send('"got-a-click"');
  });

  window.$messages = $("#messages");
  window.$uptime_value = $("#uptime-value");
});
