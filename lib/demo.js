$(document).ready(function() {
  send("document-ready");
  $("#messages").on("click", function() {
    send("clicked");
  });

  window.$messages = $("#messages");
  window.$uptime_value = $("#uptime-value");
});
