(function() {
  "use strict";
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

  // Draw bars in an svg element through d3.js
  function draw() {
    var dataset = genRandomDataset();

    var width = 750;
    var height = 450;
    var barSpace = 5;
    var barWidth = (width / dataset.length) - barSpace;

    var y_extent = [
      0,
      d3.max(dataset, function(d) {
        return d.value;
        })
      ];

    var y_scale = d3.scale.linear()
      .range([height, 0])
      .domain(y_extent);
    var height_scale = d3.scale.linear()
      .range([0, height])
      .domain(y_extent);

    d3.select("body")
      .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
          .selectAll("rect")
          .data(dataset)
          .enter()
          .append("rect")
            .attr("class", "bar")
            .attr("x", function(d, i) {
              return i*(barWidth + barSpace);
            })
            .attr("y", function(d) {
              return y_scale(d.value);
            })
            .attr("width", barWidth)
            .attr("height", function(d) {
              return height_scale(d.value);
            });
  }

  send("document-ready");
  draw();
})();
