(function() {
  "use strict";
  console.log("d3 version: " + d3.version);

  var dateFormat = d3.time.format("%Y-%m");

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
  // This is useful to test the d3.js interface in the browser
  // without gtk
  function genRandomDataset() {
    var dataset = [];

    var year = 2013;

    var minValue = 1;
    var maxValue = 20;

    function getRandomValue() {
      return getRandomInt(minValue, maxValue);
    }

    for (var month=0; month<12; month++) {
      var data = {
        "date": dateFormat(new Date(year, month)),
        "value": getRandomValue(),
      };

      dataset.push(data);
    }

    return dataset;
  }

  // Draw bars in an svg element through d3.js
  function draw(dataset) {
    // Map date strings to date objects
    dataset.forEach(function(d) {
      d.date = dateFormat.parse(d.date);
    });

    // margin, width and height defined according to the convention:
    // http://bl.ocks.org/mbostock/3019563
    var margin = {top: 20, right: 10, bottom: 30, left: 40};
    var width = 750 - margin.left - margin.right;
    var height = 450 - margin.top - margin.bottom;

    var barSpace = 5;
    var barWidth = (width / dataset.length) - barSpace;

    var xScale = d3.scale.ordinal()
      .domain(dataset.map(function(d) {
        return d.date;
      }))
      .rangeRoundBands([0, width], 0.1);

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
        .attr("width", xScale.rangeBand())
        .attr("height", function(d) {
          return heightScale(d.value);
        });

    svg.append("g")
      .selectAll("text")
      .data(dataset)
      .enter()
      .append("text")
        .attr("class", "label")
        .attr("x", function(d) {
          return xScale(d.date) + xScale.rangeBand() / 2;
        })
        .attr("y", function(d) {
            return yScale(d.value) + 16;
        })
        .text(function(d) {
          return d.value;
        });

    var xAxis = d3.svg.axis()
      .scale(xScale)
      .orient("bottom")
      .tickFormat(d3.time.format("%b"));

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

  // Make draw function available to gtk
  window.draw = draw;

  send("document-ready");

  // Uncomment to test d3.js interface in a browser
  //draw(genRandomDataset());
})();
