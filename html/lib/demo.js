(function() {
  "use strict";
  console.log("d3 version: " + d3.version);

  var dateFormat = d3.time.format("%Y-%m");

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
    var year = 2013;
    var minValue = 1;
    var maxValue = 20;

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

  // Reusable chart design as explained in:
  // http://bost.ocks.org/mike/chart/
  function barChart() {
    var margin = {top: 20, right: 40, bottom: 30, left: 40};
    var width = 750;
    var height = 450;

    var xScale = d3.scale.ordinal();
    var yScale = d3.scale.linear();
    var heightScale = d3.scale.linear();

    var xAxis = d3.svg.axis()
      .scale(xScale)
      .orient("bottom")
      .tickFormat(d3.time.format("%b"));

    var yAxis = d3.svg.axis()
      .scale(yScale)
      .orient("left");

    var default_duration = 1000;

    // Draw bars in svg element through d3.js
    function chart(selection) {
      selection.each(function(dataset) {
        var innerHeight = height - margin.top - margin.bottom;
        var innerWidth = width - margin.left - margin.right;

        // Adjust scales
        xScale.rangeRoundBands([0, innerWidth], 0.1)
          .domain(dataset.map(function(d) {
            return d.date;
          }));
        var yExtent = d3.extent(dataset, function(d) {
            return d.value;
          });
        yScale.range([innerHeight, 0])
          .domain(yExtent);
        heightScale.range([0, innerHeight])
          .domain(yExtent);

        // Bind dataset to svg element
        var svg = d3.select(this)
          .selectAll("svg")
          .data([dataset]);

        // Create svg layout if svg element doesn't exist
        var gEnter = svg.enter()
          .append("svg")
          .append("g");

        gEnter.append("g").attr("class", "x axis")
          .attr("transform", "translate(0, " + innerHeight + ")");
        gEnter.append("g").attr("class", "y axis");
        gEnter.append("g").attr("class", "bars");
        gEnter.append("g").attr("class", "labels");

        // Update dimensions
        svg.attr("width", width)
          .attr("height", height);
        svg.select("g")
          .attr("transform", "translate(" + margin.left + ", " + margin.top + ")");

        // Update axes
        svg.select(".x.axis")
          .transition()
          .duration(default_duration)
          .attr("transform", "translate(0, " + innerHeight + ")")
          .call(xAxis);

        svg.select(".y.axis")
          .transition()
          .duration(default_duration)
          .call(yAxis);

        // Bind dataset to bars
        var bars = svg.select(".bars")
          .selectAll("rect")
          .data(dataset, function(d) {
            return d.date;
          });

        // Create bars if they don't exist
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

        // Update bars
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

        // Remove bars no longer needed
        bars.exit().remove();

        // Bind dataset to labels
        var labels = svg.select(".labels")
          .selectAll(".label")
          .data(dataset, function(d) {
            return d.date;
          });

        // Create labels if they don't exist
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

        // Update labels
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

        // Remove labels no longer needed
        labels.exit().remove();
      });
    }

    chart.width = function(value) {
      if (!arguments.length) {
        return width;
      }
      width = value;
      return chart;
    };

    chart.height = function(value) {
      if (!arguments.length) {
        return height;
      }
      height = value;
      return chart;
    };

    return chart;
  }

  var body = d3.select("body");
  var chart = barChart();

  // Make draw function available to gtk
  window.draw = function(dataset) {
    // Map date strings to date objects
    dataset.forEach(function(d) {
      d.date = dateFormat.parse(d.date);
    });

    body.datum(dataset).call(chart);
  };

  // Redraw chart on window resize
  window.resize = function(width, height) {
    chart.width(width).height(height);
    body.call(chart);
  };

  send({
    "event": "document-ready"
  });

  // Uncomment to test d3.js interface in a browser
  //draw(genRandomDataset());
})();
