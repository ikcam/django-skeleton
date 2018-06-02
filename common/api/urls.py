from .routers import nested_routers, router


urlpatterns = router.urls + nested_routers
