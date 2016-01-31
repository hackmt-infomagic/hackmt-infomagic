/**
 * Created by rayde on 1/31/2016.
 */
var React = require('react');
var BarChart = require('react-chartjs').Bar;
var _ = require('underscore');

var GraphComponentAvgSeshLen = React.createClass({
    render: function(){
        var avgSeshLen = this.props.avgSeshLen;
        var labels = Object.keys(avgSeshLen).sort(function(a,b){return avgSeshLen[b]-avgSeshLen[a]});
        var data = {
            labels: labels,
            datasets: [{
                lable: 'subjects',
                fillColor: "rgba(132, 217, 227, .5)",
                strokeColor: "rgba(151,187,205,0.8)",
                highlightFill: "rgba(151,187,205,0.75)",
                highlightStroke: "rgba(151,187,205,1)",
                data: this.generateDataset()
            }]
        };
        console.log(JSON.stringify(data));
        return(
            <div className="large-12 columns">
                <BarChart className="large-12 columns" data={data} options={this.getOptions()}/>
            </div>
        );
    },
    generateDataset: function(){
        var avgSeshLen = this.props.avgSeshLen;
        var subjects = Object.keys(avgSeshLen).sort(function(a,b){return avgSeshLen[b]-avgSeshLen[a]});

        return subjects.map(function(subject) {
            return avgSeshLen[subject];
        });
    },
    getOptions: function(){
        return {
            //Boolean - Whether the scale should start at zero, or an order of magnitude down from the lowest value
            scaleBeginAtZero : true,

            //Boolean - Whether grid lines are shown across the chart
            scaleShowGridLines : true,

            //String - Colour of the grid lines
            scaleGridLineColor : "rgba(0,0,0,.05)",

            //Number - Width of the grid lines
            scaleGridLineWidth : 1,

            //Boolean - Whether to show horizontal lines (except X axis)
            scaleShowHorizontalLines: true,

            //Boolean - Whether to show vertical lines (except Y axis)
            scaleShowVerticalLines: true,

            //Boolean - If there is a stroke on each bar
            barShowStroke : true,

            //Number - Pixel width of the bar stroke
            barStrokeWidth : 2,

            //Number - Spacing between each of the X value sets
            barValueSpacing : 5,

            //Number - Spacing between data sets within X values
            barDatasetSpacing : 1,

            //String - A legend template
            legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"

        };
    }
});

module.exports = GraphComponentAvgSeshLen;
