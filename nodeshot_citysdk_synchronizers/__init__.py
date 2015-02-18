VERSION = (0, 2, 0, 'final', 0)
__version__ = VERSION


def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        version = '%s pre-alpha' % version
    else:
        if VERSION[3] != 'final':
            version = '%s %s' % (version, VERSION[3])
    return version


try:
    from .settings import NODESHOT_SYNCHRONIZERS
except:
    pass
else:
    from .citysdk_mobility import CitySdkMobility
    from .citysdk_tourism import CitySdkTourism
    from .geojson_citysdk_mobility import GeoJsonCitySdkMobility
    from .geojson_citysdk_tourism import GeoJsonCitySdkTourism
    from .openwisp_citysdk_tourism import OpenWispCitySdkTourism
    from .provinciawifi import ProvinciaWifi
    from .provinciawifi_citysdk_mobility import ProvinciaWifiCitySdkMobility
    from .provinciawifi_citysdk_tourism import ProvinciaWifiCitySdkTourism
    from .provincerometraffic import ProvinceRomeTraffic
    from .openlabor import OpenLabor
