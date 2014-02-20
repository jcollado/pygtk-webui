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

    for (var month=0; month<12; month++) {
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

    // margin, width and height defined according to the convention:
    // http://bl.ocks.org/mbostock/3019563
    var margin = {top: 20, right: 10, bottom: 30, left: 30};
    var width = 750 - margin.left - margin.right;
    var height = 450 - margin.top - margin.bottom;

    var barSpace = 5;
    var barWidth = (width / dataset.length) - barSpace;

    var xExtent = d3.extent(dataset, function(d) {
      return d.date;
    });
    var xScale = d3.time.scale()
      .range([0, width])
      .domain(xExtent);

    var yExtent = [
      0,
      d3.max(dataset, function(d) {
        return d.value;
        })
      ];
    var yScale = d3.scale.linear()
      .range([height, 0])
      .domain(yExtent);
    var heightScale = d3.scale.linear()
      .range([0, height])
      .domain(yExtent);

    var svg = d3.select("body")
      .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
          .attr("transform", "translate(" + margin.left + ", " + margin.top + ")");

    svg.append("g")
      .selectAll("rect")
      .data(dataset)
      .enter()
      .append("rect")
        .attr("class", "bar")
        .attr("x", function(d) {
          return xScale(d.date);
        })
        .attr("y", function(d) {
          return yScale(d.value);
        })
        .attr("width", barWidth)
        .attr("height", function(d) {
          return heightScale(d.value);
        });

    var xAxis = d3.svg.axis()
      .scale(xScale)
      .orient("bottom")
      .tickFormat(d3.time.format("%B"));

    svg.append("g")
      .attr("class", "axis")
      .attr("transform", "translate(0, " + height + ")")
      .call(xAxis);

    var yAxis = d3.svg.axis()
      .scale(yScale)
      .orient("left");

    svg.append("g")
      .attr("class", "axis")
      .call(yAxis);
  }

  send("document-ready");
  draw();
})();
