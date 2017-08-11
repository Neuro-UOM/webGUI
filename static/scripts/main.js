var mainApp = angular.module("mainApp", []);

namespace = '/test';
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

socket.on('connect', function() {
    socket.emit('my_event', {data: 'I\'m connected!'});
});

mainApp.controller('studentController', function($scope) {
    $scope.student = {
        firstName: "Mahesh",
        lastName: "Parashar",

        fullName: function() {
            var studentObject;
            studentObject = $scope.student;
            return studentObject.firstName + " " + studentObject.lastName;
        }
    };
    
    $scope.msg = "Message Here ";
    $scope.msg = "NEW MSG";
    
    
    
    
    socket.on('my_response', function(message) {
        $scope.msg = message.count; 
        $scope.$apply();
    });
    
    
    // https://stackoverflow.com/questions/31778139/angularjs-ng-repeat-not-printing-variable
    });