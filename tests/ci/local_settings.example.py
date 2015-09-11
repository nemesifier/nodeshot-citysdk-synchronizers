DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'nodeshot_citysdk_ci',
        'USER': 'postgres',
        'PASSWORD':  'password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

NODESHOT_CITYSDK_TOURISM_TEST_CONFIG = {
    "citysdk_category": "Testing Layer",
    "citysdk_category_id": "IDHERE",
    "citysdk_lang": "it-IT",
    "citysdk_password": "password",
    "citysdk_term": "center",
    "citysdk_type": "poi",
    "citysdk_url": "http://HOST/",
    "citysdk_username": "admin",
    "search_url": "http://HOST/pois/search"
}

NODESHOT_CITYSDK_MOBILITY_TEST_CONFIG = {
    "citysdk_url": "https://HOST/",
    "citysdk_username": "USER",
    "citysdk_password": "PASSWORD",
    "citysdk_layer": "testing.layer.name",
}
