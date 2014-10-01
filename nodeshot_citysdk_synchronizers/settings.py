from django.conf import settings


NODESHOT_SYNCHRONIZERS = getattr(settings, 'NODESHOT_SYNCHRONIZERS', [])
CITYSDK_SYNCHRONIZERS = [
    ('nodeshot_citysdk_synchronizers.OpenWispCitySdkTourism', 'OpenWISP CitySDK Tourism (periodic sync)'),
    ('nodeshot_citysdk_synchronizers.ProvinciaWifi', 'Provincia WiFi (periodic sync)'),
    ('nodeshot_citysdk_synchronizers.ProvinciaWifiCitySdkTourism', 'Provincia WiFi CitySDK Tourism (periodic sync)'),
    ('nodeshot_citysdk_synchronizers.ProvinciaWifiCitySdkMobility', 'Provincia WiFi CitySDK Mobility (periodic sync)'),
    ('nodeshot_citysdk_synchronizers.CitySdkMobility', 'CitySDK Mobility (event driven)'),
    ('nodeshot_citysdk_synchronizers.CitySdkTourism', 'CitySDK Tourism (event driven)'),
    ('nodeshot_citysdk_synchronizers.GeoJsonCitySdkMobility', 'GeoJSON CitySDK Mobility (periodic sync)'),
    ('nodeshot_citysdk_synchronizers.GeoJsonCitySdkTourism', 'GeoJSON CitySDK Tourism (periodic sync)'),
    ('nodeshot_citysdk_synchronizers.OpenLabor', 'OpenLabor (RESTful translator + event driven)'),
    ('nodeshot_citysdk_synchronizers.ProvinceRomeTraffic', 'Province of Rome Traffic')
]
setattr(settings, 'NODESHOT_SYNCHRONIZERS', NODESHOT_SYNCHRONIZERS+CITYSDK_SYNCHRONIZERS)


CITYSDK_TOURISM_TEST_CONFIG = getattr(settings, 'NODESHOT_CITYSDK_TOURISM_TEST_CONFIG', False)
CITYSDK_MOBILITY_TEST_CONFIG = getattr(settings, 'NODESHOT_CITYSDK_MOBILITY_TEST_CONFIG', False)
