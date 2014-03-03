(function() {
  "use strict";
  console.log("d3 version: " + d3.version);

  // Send data to gtk application by updating the window title
  // (this generates an event in the gtk interface)
  function send(msg) {
    document.title = JSON.stringify(msg);
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

    function getRandomValue() {
      return getRandomInt(minValue, maxValue);
    }

    for (var month=0; month<12; month++) {
      var data = {
        "date": dateFormat(new Date(year, month)),
        "value": getRandomValue(),
        "selected": false,
      };

      dataset.push(data);
    }

    return dataset;
  }

  var dateFormat = d3.time.format("%Y-%m");
  var year = 2013;

  var minValue = 1;
  var maxValue = 20;

  var xScale;
  var yScale;
  var heightScale;

  var xAxis;
  var yAxis;

  // Create svg element and draw axes
  function setup() {
    // margin, width and height defined according to the convention:
    // http://bl.ocks.org/mbostock/3019563
    var margin = {top: 20, right: 10, bottom: 30, left: 40};
    var width = 750 - margin.left - margin.right;
    var height = 450 - margin.top - margin.bottom;
    var barSpace = 5;

    xScale = d3.scale.ordinal()
      .rangeRoundBands([0, width], 0.1);

    yScale = d3.scale.linear()
      .range([height, 0]);
    heightScale = d3.scale.linear()
      .range([0, height]);

    var svg = d3.select("body")
      .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
          .attr("transform", "translate(" + margin.left + ", " + margin.top + ")");

    xAxis = d3.svg.axis()
      .scale(xScale)
      .orient("bottom")
      .tickFormat(d3.time.format("%b"));

    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0, " + height + ")");

    yAxis = d3.svg.axis()
      .scale(yScale)
      .orient("left");

    svg.append("g")
      .attr("class", "y axis");

    svg.append("g")
      .attr("id", "bars");

    svg.append("g")
      .attr("id", "labels");
  }

  // Draw bars in svg element through d3.js
  function draw(dataset) {
    console.log(dataset);

    var svg = d3.select("svg");
    var default_duration = 1000;

    // Map date strings to date objects
    dataset.forEach(function(d) {
      d.date = dateFormat.parse(d.date);
    });

    // Adjust scales
    xScale.domain(dataset.map(function(d) {
      return d.date;
    }));
    var yExtent = d3.extent(dataset, function(d) {
        return d.value;
      });
    yScale.domain(yExtent);
    heightScale.domain(yExtent);

    // Update y axis
    svg.select(".x.axis")
      .transition()
      .duration(default_duration)
      .call(xAxis);

    svg.select(".y.axis")
      .transition()
      .duration(default_duration)
      .call(yAxis);

    // Update bars
    var bars = svg.select("#bars")
      .selectAll("rect")
      .data(dataset);

    bars.enter()
      .append("rect")
        .attr("class", "bar")
        .on("click", function(d, i) {
          console.log("bar clicked: " + d.date + ", " + d.value + ", " + i);
          send({
            "event": "bar-clicked",
            "data": d,
            "index": i,
          });
        });

    bars.classed("selected", function(d) {
        return d.selected;
      })
      .transition()
      .duration(default_duration)
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

    // Update labels
    var labels = svg.select("#labels")
      .selectAll(".label")
      .data(dataset);

    labels.enter()
      .append("text")
        .attr("class", "label")
        .on("click", function(d, i) {
          console.log("label clicked: " + d.date + ", " + d.value + ", " + i);
          send({
            "event": "label-clicked",
            "data": d,
            "index": i,
          });
        });

    labels.transition()
      .duration(default_duration)
        .attr("x", function(d) {
          return xScale(d.date) + xScale.rangeBand() / 2;
        })
        .attr("y", function(d) {
            return yScale(d.value) - 5;
        })
      .text(function(d) {
        return d.value;
      });
  }

  // Make draw function available to gtk
  window.draw = draw;

  setup();
  send({
    "event": "document-ready"
  });

  // Uncomment to test d3.js interface in a browser
  //draw(genRandomDataset());
})();
