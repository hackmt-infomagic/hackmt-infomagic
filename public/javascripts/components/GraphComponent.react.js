/**
 * Created by rayde on 1/30/2016.
 */

var React = require('react');
var UserStore = require('../stores/UserStore');
var _ = require('underscore');
var GraphComponentGlobalCum = require('./GraphComponentGlobalCum.react');
var GraphComponentSubjectCum = require('./GraphComponentSubjectCum.react');
var GraphComponentSubjectToals = require('./GraphComponentSubjectTotals.react');
var GraphComponentAveSeshLen = require('./GraphComponentAvgSeshLen.react');

function getAppState(){
    return {
        user: UserStore.getUser(),
        stats: UserStore.getStats()
    }
}

var GraphComponent = React.createClass({
    getInitialState: function(){
        return getAppState();
    },
    isEmpty: function(stats){
        for(var key in stats){
            if(stats.hasOwnProperty(key)){
                return false;
            }
        }
        return true;
    },
    componentDidMount: function(){
        $(document).foundation();
        UserStore.addChangeListener(this._onChange);
    },
    componentDidUpdate: function(){
        $(document).foundation();
        UserStore.removeChangeListener(this._onChange);
    },
    render: function(){
        var stats = this.state.stats;
        if(this.isEmpty(stats)){
            return(
                <div>
                    
                </div>
            );
        }
        else {
            return(
                <div className="graph-container">
                    <div className="row">
                        <h1>Cumulative Hours</h1>
                        <GraphComponentGlobalCum isEmpty={this.isEmpty} getOptions={this.getOptions} stats={this.state.stats}/>
                    </div>
                    <div className="row">
                        <h1>Average Session Length</h1>
                        <GraphComponentAveSeshLen avgSeshLen={this.state.stats['average_session_lengths']}/>
                    </div>
                    <div className="row">
                        <h1>Subject Totals</h1>
                        <GraphComponentSubjectToals isEmpty={this.isEmpty} subjects={this.state.user.subjects}
                                                    subjectTotals={this.state.stats['subject_totals']} />
                    </div>)
                    <div className="row">
                        <h1>Subject Cumulative</h1>
                        <GraphComponentSubjectCum isEmpty={this.isEmpty} getOptions={this.getOptions} stats={this.state.stats}
                                                  subjects={this.state.user.subjects}/>
                    </div>
                </div>
            );
        }
    },

    getOptions: function(){
      return {
          ///Boolean - Whether grid lines are shown across the chart
          scaleShowGridLines : true,

          //String - Colour of the grid lines
          scaleGridLineColor : "rgba(0,0,0,.05)",

          //Number - Width of the grid lines
          scaleGridLineWidth : 1,

          //Boolean - Whether to show horizontal lines (except X axis)
          scaleShowHorizontalLines: true,

          //Boolean - Whether to show vertical lines (except Y axis)
          scaleShowVerticalLines: true,

          //Boolean - Whether the line is curved between points
          bezierCurve : true,

          //Number - Tension of the bezier curve between points
          bezierCurveTension : 0.4,

          //Boolean - Whether to show a dot for each point
          pointDot : true,

          //Number - Radius of each point dot in pixels
          pointDotRadius : 4,

          //Number - Pixel width of point dot stroke
          pointDotStrokeWidth : 1,

          //Number - amount extra to add to the radius to cater for hit detection outside the drawn point
          pointHitDetectionRadius : 20,

          //Boolean - Whether to show a stroke for datasets
          datasetStroke : true,

          //Number - Pixel width of dataset stroke
          datasetStrokeWidth : 2,

          //Boolean - Whether to fill the dataset with a colour
          datasetFill : true,

          //String - A legend template
          legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].strokeColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"

      };
    },
    _onChange: function(){
        this.setState(getAppState());
    }
});

module.exports = GraphComponent;
