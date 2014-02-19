$(document).ready(function() {
  function send(msg) {
    document.title = "null";
    document.title = msg;
  }

  send("document-ready");
  $("#messages").on("click", function() {
    send("clicked");
  });

  window.$messages = $("#messages");
  window.$uptime_value = $("#uptime-value");
});
