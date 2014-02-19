(function() {
  console.log("d3 version: " + d3.version);

  // Send data to gtk application by updating the window title
  // (this generates an event in the gtk interface)
  function send(msg) {
    document.title = "null";
    document.title = msg;
  }

  // Returns a random integer between min and max
  // Using Math.round() will give you a non-uniform distribution!
  function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min);
  }

  // Generate random data to plot
  function genRandomDataset() {
    var dataset = [];
    var minValue = 1;
    var maxValue = 20;

    function getRandomValue() {
      return getRandomInt(minValue, maxValue);
    }

    for (var month=1; month<=12; month++) {
      var data = {
        "date": new Date(2013, month),
        "value": getRandomValue(),
      };

      dataset.push(data);
    }

    return dataset;
  }

  var dataset = genRandomDataset();

  d3.select("body")
    .append("div")
      .selectAll("p")
      .data(dataset)
      .enter()
      .append("p")
        .text(function(d) {
          return "date: " + d.date + ", value: " + d.value;
        });

  send("document-ready");
})();
