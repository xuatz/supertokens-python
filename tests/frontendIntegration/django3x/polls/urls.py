from django.urls import path

from tests.frontendIntegration.django3x.polls import views

urlpatterns = [
    path('index.html', views.send_file, name='index.html'),
    path('login', views.login, name='login'),
    path('beforeeach', views.before_each, name='beforeeach'),
    path('testUserConfig', views.test_config, name='testUserConfig'),
    path(
        'multipleInterceptors',
        views.multiple_interceptors,
        name='multipleInterceptors'),
    path('', views.get_info, name='/'),
    path('update-jwt', views.update_jwt, name='update_jwt'),
    path('testing', views.testing, name='testing'),
    path('logout', views.logout, name='logout'),
    path('revokeAll', views.revoke_all, name='revokeAll'),
    path('refresh', views.refresh, name='refresh'),
    path(
        'refreshAttemptedTime',
        views.refresh_attempted_time,
        name='refreshAttemptedTime'),
    path('auth/session/refresh', views.refresh, name='refresh'),
    path('setAntiCsrf', views.set_anti_csrf, name='setAntiCsrf'),
    path('setEnableJWT', views.set_enable_jwt, name='setEnableJWT'),
    path('featureFlags', views.feature_flags, name='featureFlags'),
    path('reinitialiseBackendConfig', views.reinitialize, name='reinitialiseBackendConfig'),
    path(
        'refreshCalledTime',
        views.refresh_called_time,
        name='refreshCalledTime'),
    path(
        'getSessionCalledTime',
        views.get_session_called_time,
        name='getSessionCalledTime'),
    path('ping', views.ping, name='ping'),
    path('testHeader', views.test_header, name='testHeader'),
    path('checkDeviceInfo', views.check_device_info, name='checkDeviceInfo'),
    path('check-rid', views.check_rid, name='check-rid'),
    path('checkAllowCredentials',
         views.check_allow_credentials,
         name='checkAllowCredentials'),
    path('testError', views.test_error, name='testError'),
]
