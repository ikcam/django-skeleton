angular.module('app', ['angularMoment'])

.run(function(amMoment) {
	amMoment.changeLocale(site_language);
})

.controller('TableController', function($scope, $http){
    $scope.data = null;
    $scope.currPage = 1;
    $scope.numPages = 1;
    $scope.ordering = null;

    $scope.setUrl = function(url){
        $scope.url = url;
        $scope.fetch();
    };

    $scope.nextPage = function(){
        if($scope.data.next){
            $scope.currPage = $scope.currPage + 1;
            $scope.setUrl($scope.data.next);
        }
    };

    $scope.previousPage = function(){
        if($scope.data.previous){
            $scope.currPage = $scope.currPage - 1;
            $scope.setUrl($scope.data.previous);
        }
    };

    $scope.setFilter = function(filter, value){
        var f = getParameterByName(filter, $scope.url);

        if(f == undefined){
            var url = $scope.url;
            var newUrl = url + '&'+ filter + '=' + value;
            $scope.setUrl(newUrl);
        } else if(value == undefined){

        } else {
            var url = $scope.url;
            var newUrl = url.replace(filter + '=' + f, filter + '=' + value)
            $scope.setUrl(newUrl);
        }
    }

    $scope.orderList = function(variable){
        // Get order var if exists
        var o = getParameterByName('o', $scope.url);

        if(variable == o){
            var url = $scope.url;
            $scope.ordering = '-' + variable;
            var newURL = url.replace(/(o=).*?(&|$)/,'$1' + $scope.ordering + '$2');

            $scope.setUrl(newURL);
        } else if(o != undefined) {
            var url = $scope.url;
            $scope.ordering = variable;
            var newURL = url.replace(/(o=).*?(&|$)/,'$1' + $scope.ordering + '$2');

            $scope.setUrl(newURL);
        } else{
            $scope.ordering = variable;
            var newURL = $scope.url + '&o=' + $scope.ordering;
            $scope.setUrl(newURL);
        }
    };

    $scope.fetch = function(){
        $http({method: 'GET', url: $scope.url})
            .then(function(response) {
                $scope.status = response.status;
                $scope.data = response.data;
                // Set numPages
                var count = $scope.data.count;
                if(count % 10 == 0){
                    $scope.numPages = count / 10;
                } else if(count < 10) {
                    $scope.numPages = 1;
                } else{
                    $scope.numPages = parseInt(count / 10) + 1;
                }
            }, function(response) {
                $scope.data = response.data || 'Request failed';
                $scope.status = response.status;
            });
    };

    var getParameterByName = function(name, url) {
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }
});

angular.element(function(){
    angular.bootstrap(document.querySelector('#mainContent'), ['app']);
});
