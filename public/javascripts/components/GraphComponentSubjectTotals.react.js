/**
 * Created by rayde on 1/31/2016.
 */
var React = require('react');
var BarChart = require('react-chartjs').Bar;
var _ = require('underscore');

var GraphComponentSubjectTotals = React.createClass({
    render: function(){
        var subjectTotals = this.props.subjectTotals;
        var labels = Object.keys(subjectTotals).sort(function(a,b){return subjectTotals[b]-subjectTotals[a]});
        var data = {
            labels: labels,
            datasets: [{
                lable: 'subjects',
                fillColor: "rgba(132, 217, 227, .5)",
                strokeColor: "rgba(20, 49, 73, .4)",
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
        var subjectTotals = this.props.subjectTotals;
        var subjects = Object.keys(subjectTotals).sort(function(a,b){return subjectTotals[b]-subjectTotals[a]});

        return subjects.map(function(subject) {
            return subjectTotals[subject];
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
    },
    setScale: function(options){
        var scaleOptions = {
            scaleOverride: true,
            scaleSteps: 20,
            scaleStepWidth: Math.ceil((this.findMax()/20)/10)*10,
            scaleStartValue: 0
        };
        _.extend(scaleOptions, options);
        return scaleOptions;
    },
    findMax: function(){

    }
});

module.exports = GraphComponentSubjectTotals;