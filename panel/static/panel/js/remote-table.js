/* global angular */
angular
  .module('RemoteTable', ['angularMoment'])
  .value('LANGUAGE', angular.element('html').attr('lang'))
  .run(['amMoment', 'LANGUAGE', function (amMoment, LANGUAGE) {
    amMoment.changeLocale(LANGUAGE)
  }])
  .controller('TableController', ['$http', '$scope', function ($http, $scope) {
    $scope.data = null
    $scope.currPage = 1
    $scope.numPages = 1
    $scope.loading = false
    $scope.ordering = null

    $scope.setUrl = function (url) {
      if ($scope.loading) return

      $scope.url = url
      $scope.fetch()
    }

    $scope.nextPage = function () {
      if ($scope.loading) return

      if ($scope.data.next) {
        $scope.currPage = $scope.currPage + 1
        $scope.setUrl($scope.data.next)
      }
    }

    $scope.previousPage = function () {
      if ($scope.loading) return

      if ($scope.data.previous) {
        $scope.currPage = $scope.currPage - 1
        $scope.setUrl($scope.data.previous)
      }
    }

    $scope.setFilter = function (filter, value) {
      if ($scope.loading) return

      var f = getParameterByName(filter, $scope.url)
      var url
      var newUrl

      if (f === undefined) {
        url = $scope.url
        newUrl = url + '&' + filter + '=' + value
        $scope.setUrl(newUrl)
      } else if (value === undefined) {

      } else {
        url = $scope.url
        newUrl = url.replace(filter + '=' + f, filter + '=' + value)
        $scope.setUrl(newUrl)
      }
    }

    $scope.orderList = function (variable) {
      if ($scope.loading) return

      // Get order var if exists
      var o = getParameterByName('o', $scope.url)
      var url
      var newURL

      if (variable === o) {
        url = $scope.url
        $scope.ordering = '-' + variable
        newURL = url.replace(/(o=).*?(&|$)/, '$1' + $scope.ordering + '$2')
      } else if (o !== undefined) {
        url = $scope.url
        $scope.ordering = variable
        newURL = url.replace(/(o=).*?(&|$)/, '$1' + $scope.ordering + '$2')
      } else {
        $scope.ordering = variable
        newURL = $scope.url + '&o=' + $scope.ordering
      }

      $scope.setUrl(newURL)
    }

    $scope.fetch = function () {
      $http({
        method: 'GET',
        url: $scope.url
      })
        .then(function (response) {
          $scope.loading = false
          $scope.data = response.data
          $scope.status = response.status
          // Set numPages
          var count = $scope.data.count
          if (count % 10 === 0) {
            $scope.numPages = count / 10
          } else if (count < 10) {
            $scope.numPages = 1
          } else {
            $scope.numPages = parseInt(count / 10) + 1
          }
        }, function (response) {
          $scope.data = response.data || 'Request failed'
          $scope.loading = false
          $scope.status = response.status
        })
    }

    var getParameterByName = function (name, url) {
      name = name.replace(/[[\]]/g, '\\$&')
      var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)')
      var results = regex.exec(url)
      if (!results) return null
      if (!results[2]) return ''
      return decodeURIComponent(results[2].replace(/\+/g, ' '))
    }
  }])
