/**
 * Created by rayde on 1/30/2016.
 */
var React = require('react');
var LineChart = require('react-chartjs').Line;
var _ = require('underscore');

var GraphComponentGlobalCum = React.createClass({
    render: function(){
        var stats = this.props.stats;
        if(this.props.isEmpty(stats)){
            return (<div>loading data...</div>);
        }
        else{
            var stat_field = stats['global_cumulative'];
            var label = stat_field.map(function(stat){
                //return "bucket " + stat_field.indexOf(stat);
                return '';
            });
            var data = {
                labels: label,
                datasets: [{
                    label: "My First dataset",
                    fillColor: "rgba(132, 217, 227, .2)",
                    strokeColor: "rgba(220,220,220,1)",
                    pointColor: "rgba(20, 49, 73, .8)",
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(220,220,220,1)",
                    data: stat_field
                }]
            };
            return (
                <div className="large-12 columns" >
                    <LineChart className="large-12 columns" data={data} options={this.setScale(this.props.getOptions())} />
                </div>
            );
        }
    },
    setScale: function(options){
        var data = this.props.stats['global_cumulative'];
        var scaleOptions = {
            scaleOverride: true,
            scaleSteps: 20,
            scaleStepWidth: Math.ceil((data[data.length-1]/20)/10) * 10,
            scaleStartValue: 0
        };
        _.extend(scaleOptions, options);
        return scaleOptions;
    }
});


module.exports = GraphComponentGlobalCum;