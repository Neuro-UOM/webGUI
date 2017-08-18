var mainApp = angular.module("mainApp",['nvd3','ui.bootstrap']);

namespace = '/test';
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

socket.on('connect', function() {
     socket.emit('my_event', {data: 'I\'m connected!'});
});

mainApp.controller('mainController', function($scope) {
    
    $scope.student = {
        firstName: "Mahesh",
        lastName: "Parashar",

        fullName: function() {
            var studentObject;
            studentObject = $scope.student;
            return studentObject.firstName + " " + studentObject.lastName;
        }
    };
    
    // jinja {{}}} => https://stackoverflow.com/questions/31778139/angularjs-ng-repeat-not-printing-variable
});

mainApp.controller('freqController', function($scope) {
    
    var black = { "color" : "white","background-color" : "black"}
    var white = { "color" : "black","background-color" : "white"}
                
    $scope.styleTiles = [black, black, black];
    $scope.count = [true, true, true] //[0,0,0];
    $scope.freqTiles = [8,10,12];  // 5,10,20
    
    var isRunning = true;
    var intervalID = [0,0,0];
    
    $scope.changeRunState = function(){
        if(isRunning){
            for (i = 0; i < $scope.freqTiles.length; i += 1) {
                (function(i) {
                    
                    intervalID[i] = setInterval(function(){ 
                                        if ($scope.count[i]){
                                            $scope.styleTiles[i] = white;
                                            $scope.$apply();
                                        }
                                        else{
                                            $scope.styleTiles[i] = black; 
                                            $scope.$apply();
                                        }
                                        $scope.count[i] = !$scope.count[i];
                                        //console.log(Date());  //-> Sum of Freqs.
                                    }, 1000/$scope.freqTiles[i])
                })(i);
            }
        }
        else{
            for (i = 0; i < $scope.freqTiles.length; i += 1) {
                clearInterval(intervalID[i]);
            }
        }
        isRunning = !isRunning;
    }
    
    // Intial Start
    $scope.changeRunState();
});

mainApp.controller('chartController', function($scope) {
    $scope.dataA = [123213,123123,123,23,34,34,5,232,34];
    $scope.newData = [];

    for (var j = 0 ; j < 100; j++){
        $scope.dataA.push(0);
    }

    console.log("inside chart");
    socket.on('fourier_response', function(message) {
        //  console.log(message.data);

        $scope.dataA = message.data;
        //  var dataArr = message.raw_array;
        
        //  for(i=0; i< $scope.nodeVal.length; i++){
        //    $scope.nodeVal[i] = dataArr[i];
        //  }
        //  $scope.$apply();

        $scope.newData = [];
        for (var i = $scope.dataA.length - 100, j = 0 ; i < $scope.dataA.length, j < 100; i++ , j++){
           if (parseFloat($scope.dataA[i]) != NaN){
                $scope.newData.push( { x : j , y : parseFloat($scope.dataA[i])});
                // console.log($scope.newData.length);
           }
        }

        console.log($scope.newData);

        $scope.options = {
            chart: {
                type: 'sparklinePlus',
                height: 450,
                x: function(d, i){return i;},
                xTickFormat: function(d) {
                    return $scope.newData[d].x
                },
                duration: 250
            }
        };

        $scope.data = $scope.newData;

        $scope.$apply();
    });
    
    
});

mainApp.controller('nodesController', function($scope) {
    
    $scope.nodes = ['P7', 'P8', 'T7', 'T8', 'O1', 'O2'];
    $scope.nodeVal = [0,0,0,0,0,0];
    
    socket.on('raw_response', function(message) {
        //  console.log(message.raw_array[0]);

         var dataArr = message.raw_array;
        
         for(i=0; i< $scope.nodeVal.length; i++){
           $scope.nodeVal[i] = dataArr[i];
         }
         $scope.$apply();
    });
});