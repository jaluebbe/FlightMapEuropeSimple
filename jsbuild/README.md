# This describes how to create a minified stripped-down version of turf.js .

At first install browserify and uglify.

```
npm install -g browserify uglify
```

Install all required turf.js modules.
```
npm install @turf/meta @turf/great-circle @turf/distance @turf/helpers @turf/boolean-point-in-polygon
```

Create my_turf.min.js .
```
browserify main.js -s turf|uglifyjs -cm > ../static/my_turf.min.js
```
