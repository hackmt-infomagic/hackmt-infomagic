/**
 * Created by rayde on 1/30/2016.
 */
var React = require('react');
var LineChart = require('react-chartjs').Line;
var _ = require('underscore');

var GraphComponentSubjectCum = React.createClass({
    render: function(){
        var stats = this.props.stats;
        if(this.props.isEmpty(stats)){
            return (<div>loading data...</div>);
        }
        else {
            var stat_field = this.props.stats['subject_cumulatives'][this.props.subjects[0]];
            var label = stat_field.map(function(subject){
                //return "bucket " + stat_field.indexOf(stat);
                return '';
            });

            var data = {
                    labels: label,
                    datasets: this.generateDatasets(this.props.subjects)
            };
            return(
                <div className="large-12 columns">
                    <LineChart className="large-12 columns" data={data} options={this.setScale(this.props.getOptions())} />
                </div>
            );
        }
    },
    generateDatasets: function(subjects){
        var subjectCum = this.props.stats['subject_cumulatives'];
        return subjects.map(function(subject){
            return {
                label: subject,
                fillColor: "rgba(132, 217, 227, .1)",
                strokeColor: "rgba(151,187,205,1)",
                pointColor: "rgba(20, 49, 73, .8)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(151,187,205,1)",
                data: subjectCum[subject]
            };
        });
    },

    findMax: function(){
        var max = 0;
        var subjectTotals = this.props.stats['subject_totals'];
        for(var key in subjectTotals){
            if(subjectTotals.hasOwnProperty(key)){
                if(subjectTotals[key] > max){
                    max = subjectTotals[key];
                }
            }
        }
        return max;
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
    }
});


module.exports = GraphComponentSubjectCum;
