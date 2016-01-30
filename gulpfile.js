/**
 * Created by rayde on 12/24/2015.
 */

var gulp = require('gulp');
var plugins = require('gulp-load-plugins')();
var browserify = require('browserify');
var watchify = require('watchify');
var reactify = require('reactify');
var source = require('vinyl-source-stream');
var del = require('del');

var sassPaths = [
    'bower_components/foundation-sites/scss',
    'bower_components/motion-ui/src'
];

var reactPath = './public/javascripts/app.js';

gulp.task('clean', function(done){
    del(['build'], done);
});

gulp.task('sass', function() {
    return gulp.src('public/stylesheets/app.scss')
        .pipe(plugins.sass({
                includePaths: sassPaths
            })
            .on('error', plugins.sass.logError))
        .pipe(plugins.autoprefixer({
            browsers: ['last 2 versions', 'ie >= 9']
        }))
        .pipe(gulp.dest('public/build'));
});

gulp.task('react', function() {
    browserify(reactPath)
        .transform(reactify)
        .bundle()
        .pipe(source('bundle.js'))
        .pipe(gulp.dest('public/build'));
});

gulp.task('watch', function(){
    gulp.watch(['public/**/*.scss'], ['sass']);
    gulp.watch(['public/**/*.js','!public/build/*.js'], ['react']);
});

gulp.task('default', ['watch', 'sass', 'react']);