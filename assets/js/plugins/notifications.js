angular.module('appAsyncContent', ['angularMoment'])

.run(function(amMoment) {
	amMoment.changeLocale(site_language);
})

.controller('RemoteController', function($scope, $http){
  $scope.data = null;
  $scope.loading = false;
  $scope.url = null;

  $scope.setUrl = function(url){
    if ($scope.loading) return;

    $scope.url = url;
    $scope.fetch();
  }

  $scope.fetch = function(){
    $scope.loading = true;

    $http.get($scope.url)
      .then(function(response){
        $scope.data = response.data.results;
        $scope.loading = false;
      }, function(err){
        $scope.loading = false;
      });
  }
});
