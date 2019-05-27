angular
    .module('NotificationWidget', ['angularMoment'])
    .config(['$httpProvider', function($httpProvider){
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }])
    .value('LANGUAGE', angular.element('html').attr('lang'))
    .factory('NotificationService', ['$http', 'LANGUAGE', function($http, LANGUAGE){
        return {
            list: function(url){
                if(url)
                    return $http.get(url);
                else
                    return $http.get(`/api/panel/notifications/`);
            },
            setAllRead: function(pk){
                return $http.post(`/api/panel/notifications/set-all-read/`);
            },
            setRead: function(pk){
                return $http.post(`/api/panel/notifications/${pk}/set-read/`);
            }
        }
    }])
    .run(['amMoment', 'LANGUAGE', function (amMoment, LANGUAGE) {
        amMoment.changeLocale(LANGUAGE);
    }])

    .controller('NotificationListController', ['$scope', '$timeout', 'NotificationService', function ($scope, $timeout, NotificationService) {
        $scope.loading = true;

        $scope.loadMore = function(){
            if($scope.loading || !$scope.notificationList.next) return;

            $scope.loading = true;

            NotificationService
                .list($scope.notificationList.next)
                .then(function(response){
                    results = $scope.notificationList.results.chain(response.data.results);
                    $scope.notificationList = response.data;
                    $scope.notificationList.results = results;
                    $scope.loading = false;
                });
        }

        $scope.setReadAll = function(){
            $scope.loading = true;
            NotificationService
                .setAllRead()
                .then(function(){
                    $scope.loading = false;
                });
        }

        $scope.loadNotifications = function(){
            NotificationService
            .list()
            .then(function(response){
                $scope.notificationList = response.data;
                $scope.loading = false;
            });
        }
    }]);
