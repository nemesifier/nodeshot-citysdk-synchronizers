import simplejson as json
import requests
from datetime import date, timedelta
from time import sleep

from django.core import management
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point, GEOSGeometry
from django.test import TestCase

from nodeshot.core.layers.models import Layer
from nodeshot.core.base.tests import user_fixtures
from nodeshot.interop.sync.models import LayerExternal, NodeExternal
from nodeshot.core.nodes.models import Node
from nodeshot.interop.sync.tests import capture_output

from nodeshot_citysdk_synchronizers.settings import settings, CITYSDK_TOURISM_TEST_CONFIG, CITYSDK_MOBILITY_TEST_CONFIG


TEST_FILES_PATH = '%snodeshot/testing' % settings.STATIC_URL


class CitySdkSyncTest(TestCase):
    """ tests for nodeshot_citysdk_synchronizers package """
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json'
    ]

    def test_provinciawifi(self):
        """ test ProvinciaWifi synchronizer """
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = 'POINT (12.0 42.0)'
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot_citysdk_synchronizers.ProvinciaWifi'
        external._reload_schema()
        external.url = '%s/provincia-wifi.xml' % TEST_FILES_PATH
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('5 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('5 total external', output)
        self.assertIn('5 total local', output)

        # start checking DB too
        nodes = layer.node_set.all()

        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 5)

        # check one particular node has the data we expect it to have
        node = Node.objects.get(slug='viale-di-valle-aurelia-73')
        self.assertEqual(node.name, 'viale di valle aurelia, 73')
        self.assertEqual(node.address, 'viale di valle aurelia, 73, Roma')
        point = Point(12.4373, 41.9025)
        self.assertTrue(node.geometry.equals(point))

        # ensure itmes with the same name on the XML get a different name in the DB
        node = Node.objects.get(slug='largo-agostino-gemelli-8')
        node = Node.objects.get(slug='largo-agostino-gemelli-8-2')
        node = Node.objects.get(slug='largo-agostino-gemelli-8-3')
        node = Node.objects.get(slug='largo-agostino-gemelli-8-4')

        ### --- with the following step we expect some nodes to be deleted and some to be added --- ###

        external.url = '%s/provincia-wifi2.xml' % TEST_FILES_PATH
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('1 nodes added', output)
        self.assertIn('2 nodes unmodified', output)
        self.assertIn('3 nodes deleted', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('3 total external', output)
        self.assertIn('3 total local', output)

        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 3)

        # check one particular node has the data we expect it to have
        node = Node.objects.get(slug='via-g-pullino-97')
        self.assertEqual(node.name, 'Via G. Pullino 97')
        self.assertEqual(node.address, 'Via G. Pullino 97, Roma')
        self.assertEqual(node.description, 'Indirizzo: Via G. Pullino 97, Roma; Tipologia: Privati federati')
        point = Point(12.484, 41.8641)
        self.assertTrue(node.geometry.equals(point))

    def test_province_rome_traffic(self):
        """ test ProvinceRomeTraffic converter """
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = 'POINT (12.0 42.0)'
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        streets_url = '%s/citysdk-wp4-streets.json' % TEST_FILES_PATH
        measurements_url = '%s/citysdk-wp4-measurements.json' % TEST_FILES_PATH

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot_citysdk_synchronizers.ProvinceRomeTraffic'
        external._reload_schema()
        external.config = {
            "streets_url": streets_url,
            "measurements_url": measurements_url,
            "check_streets_every_n_days": 2
        }
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('20 streets added', output)
        self.assertIn('0 streets changed', output)
        self.assertIn('20 total external', output)
        self.assertIn('20 total local', output)
        self.assertIn('Updated measurements of 4 street segments', output)

        # start checking DB too
        nodes = layer.node_set.all()

        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 20)

        # check one particular node has the data we expect it to have
        node = Node.objects.get(slug='via-di-santa-prisca')
        self.assertEqual(node.name, 'VIA DI SANTA PRISCA')
        self.assertEqual(node.address, 'VIA DI SANTA PRISCA')
        geometry = GEOSGeometry('SRID=4326;LINESTRING (12.4837894439700001 41.8823699951170028, 12.4839096069340005 41.8820686340329971, 12.4839801788330007 41.8818206787110014)')
        self.assertTrue(node.geometry.equals(geometry))

        # check measurements
        node = Node.objects.get(slug='via-casilina')
        self.assertEqual(node.name, 'VIA CASILINA')
        self.assertEqual(node.data['last_measurement'], '09-09-2013 22:31:00')
        self.assertEqual(node.data['velocity'], '44')

        # ensure last_time_streets_checked is today
        layer = Layer.objects.get(pk=layer.id)
        self.assertEqual(layer.external.config['last_time_streets_checked'], str(date.today()))

        ### --- not much should happen --- ###

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('Street data not processed', output)

        # set last_time_streets_checked to 6 days ago
        layer.external.config['last_time_streets_checked'] = str(date.today() - timedelta(days=6))
        external.full_clean()
        layer.external.save()

        ### --- with the following step we expect some nodes to be deleted and some to be added --- ###

        streets_url = '%s/citysdk-wp4-streets2.json' % TEST_FILES_PATH
        measurements_url = '%s/citysdk-wp4-measurements2.json' % TEST_FILES_PATH

        external.config['streets_url'] = streets_url
        external.config['measurements_url'] = measurements_url
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('5 streets added', output)
        self.assertIn('16 streets unmodified', output)
        self.assertIn('4 streets deleted', output)
        self.assertIn('0 streets changed', output)
        self.assertIn('21 total external', output)
        self.assertIn('21 total local', output)
        self.assertIn('No measurements found', output)

        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 21)

        # ensure last_time_streets_checked is today
        layer = Layer.objects.get(pk=layer.id)
        self.assertEqual(layer.external.config['last_time_streets_checked'], str(date.today()))


    def test_openlabor_get_nodes(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = 'POINT (12.0 42.0)'
        layer.new_nodes_allowed = True
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot_citysdk_synchronizers.OpenLabor'
        external._reload_schema()
        external.config = {
            "open311_url": '%s/' % TEST_FILES_PATH,
            "service_code_get": "001",
            "service_code_post": "002",
            "default_status": "active",
            "api_key": "DEVO1395445966"
        }
        external.full_clean()
        external.save()

        url = reverse('api_layer_nodes_list', args=[layer.slug])
        response = self.client.get(url)
        nodes = response.data['nodes']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0]['name'], 'SARTO CONFEZIONISTA')
        self.assertEqual(nodes[0]['address'], 'Via Lussemburgo snc, Anzio - 00042')

        # test geojson
        url = reverse('api_layer_nodes_geojson', args=[layer.slug])
        response = self.client.get(url)
        nodes = response.data['features']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0]['properties']['name'], 'SARTO CONFEZIONISTA')
        self.assertEqual(nodes[0]['properties']['address'], 'Via Lussemburgo snc, Anzio - 00042')

    def test_openlabor_add_node(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = 'POINT (12.0 42.0)'
        layer.new_nodes_allowed = True
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        url = 'http://devopenlabor.lynxlab.com/api/v1'

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot_citysdk_synchronizers.OpenLabor'
        external._reload_schema()
        external.config = {
            "open311_url": url,
            "service_code_get": "001",
            "service_code_post": "002",
            "default_status": "active",
            "api_key": "DEVO1395445966"
        }
        external.full_clean()
        external.save()

        node = Node()
        node.name = 'offerta di lavoro di test'
        node.description = 'altra offerta di lavoro inserita automaticamente tramite unit test'
        node.geometry = 'POINT (12.5823391919000012 41.8721429276999820)'
        node.layer = layer
        node.user_id = 1
        node.address = 'via del test'
        node.data = {
            "professional_profile": "professional_profile test",
            "qualification_required": "qualification_required test",
            "contract_type": "contract_type test",
            "zip_code": "zip code test",
            "city": "city test"
        }

        node.save()
        self.assertIsNotNone(node.external.external_id)

    def test_openwisp_citysdk_tourism(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = 'POINT (12.0 42.0)'
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        xml_url = '%s/openwisp-georss.xml' % TEST_FILES_PATH

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot_citysdk_synchronizers.OpenWispCitySdkTourism'
        external._reload_schema()
        external.config = CITYSDK_TOURISM_TEST_CONFIG.copy()
        external.config.update({
            "status": "active",
            "url": xml_url,
            "verify_ssl": False
        })
        external.full_clean()
        external.save()

        querystring_params = {
            'category': CITYSDK_TOURISM_TEST_CONFIG['citysdk_category'],
            'limit': '-1'
        }

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 0)

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('42 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('42 total external', output)
        self.assertIn('42 total local', output)

        sleep(1)  # wait 1 second

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 42)

        ### --- with the following step we expect some nodes to be deleted --- ###

        xml_url = '%s/openwisp-georss2.xml' % TEST_FILES_PATH
        external.config['url'] = xml_url
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('4 nodes unmodified', output)
        self.assertIn('38 nodes deleted', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('4 total external', output)
        self.assertIn('4 total local', output)

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 4)

        ### --- delete everything --- ###

        for node in layer.node_set.all():
            node.delete()

        sleep(1)  # wait 1 second

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 0)

    def test_geojson_citysdk_tourism(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = 'POINT (12.0 42.0)'
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        url = '%s/geojson1.json' % TEST_FILES_PATH

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot_citysdk_synchronizers.GeoJsonCitySdkTourism'
        external._reload_schema()
        external.config = CITYSDK_TOURISM_TEST_CONFIG.copy()
        external.config.update({
            "status": "active",
            "url": url,
            "verify_ssl": False
        })
        external.full_clean()
        external.save()

        querystring_params = {
            'category': CITYSDK_TOURISM_TEST_CONFIG['citysdk_category'],
            'limit': '-1'
        }

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 0)

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('2 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)
        self.assertEqual(layer.node_set.count(), 2)

        sleep(1)  # wait 1 second

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 2)

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('2 nodes unmodified', output)
        self.assertIn('0 nodes deleted', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)
        self.assertEqual(layer.node_set.count(), 2)

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 2)

        ### --- repeat with slightly different input --- ###

        url = '%s/geojson4.json' % TEST_FILES_PATH
        external.config['url'] = url
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('1 nodes unmodified', output)
        self.assertIn('1 nodes deleted', output)
        self.assertIn('1 total external', output)
        self.assertIn('1 total local', output)
        self.assertEqual(layer.node_set.count(), 1)

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 1)

        ### --- delete everything --- ###

        for node in layer.node_set.all():
            node.delete()

        sleep(1)  # wait 1 second

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 0)

    def test_provinciawifi_citysdk_tourism(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = 'POINT (12.0 42.0)'
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        xml_url = '%s/provincia-wifi.xml' % TEST_FILES_PATH

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot_citysdk_synchronizers.ProvinciaWifiCitySdkTourism'
        external._reload_schema()
        external.config = CITYSDK_TOURISM_TEST_CONFIG.copy()
        external.config.update({
            "status": "active",
            "url": xml_url,
            "verify_ssl": False
        })
        external.full_clean()
        external.save()

        querystring_params = {
            'category': CITYSDK_TOURISM_TEST_CONFIG['citysdk_category'],
            'limit': '-1'
        }

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 0)

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('5 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('5 total external', output)
        self.assertIn('5 total local', output)
        self.assertEqual(layer.node_set.count(), 5)

        sleep(1)

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 5)

        ### --- with the following step we expect some nodes to be deleted and some to be added --- ###

        external.config['url'] = '%s/provincia-wifi2.xml' % TEST_FILES_PATH
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('1 nodes added', output)
        self.assertIn('2 nodes unmodified', output)
        self.assertIn('3 nodes deleted', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('3 total external', output)
        self.assertIn('3 total local', output)
        self.assertEqual(layer.node_set.count(), 3)

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 3)

        sleep(1)

        ### --- delete everything --- ###

        for node in layer.node_set.all():
            node.delete()

        sleep(1)  # wait 1 second

        data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
        self.assertEqual(len(data['poi']), 0)

    def test_geojson_citysdk_mobility(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = 'POINT (12.0 42.0)'
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        url = '%s/geojson1.json' % TEST_FILES_PATH

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot_citysdk_synchronizers.GeoJsonCitySdkMobility'
        external._reload_schema()
        external.config = CITYSDK_MOBILITY_TEST_CONFIG.copy()
        external.config.update({
            "url": url,
            "verify_ssl": False,
        })
        external.full_clean()
        external.save()

        querystring_params = {
            'layer': CITYSDK_MOBILITY_TEST_CONFIG['citysdk_layer'],
            'per_page': '1000'
        }
        citysdk_nodes_url = '%s/nodes' % CITYSDK_MOBILITY_TEST_CONFIG['citysdk_url']
        data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
        self.assertEqual(len(data['results']), 0)

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('2 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)
        self.assertEqual(layer.node_set.count(), 2)
        self.assertNotEqual(layer.node_set.first().external.external_id, '')

        sleep(1)  # wait 1 second

        data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
        self.assertEqual(len(data['results']), 2)

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('2 nodes unmodified', output)
        self.assertIn('0 nodes deleted', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)
        self.assertEqual(layer.node_set.count(), 2)

        data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
        self.assertEqual(len(data['results']), 2)

        ### --- repeat with slightly different input --- ###

        url = '%s/geojson4.json' % TEST_FILES_PATH
        external.config['url'] = url
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('1 nodes unmodified', output)
        self.assertIn('1 nodes deleted', output)
        self.assertIn('1 total external', output)
        self.assertIn('1 total local', output)
        self.assertEqual(layer.node_set.count(), 1)

        data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
        self.assertEqual(len(data['results']), 1)

        ### --- delete everything --- ###

        for node in layer.node_set.all():
            node.delete()

        sleep(1)  # wait 1 second

        data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
        self.assertEqual(len(data['results']), 0)

    def test_provinciawifi_citysdk_mobility(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = 'POINT (12.0 42.0)'
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        xml_url = '%s/provincia-wifi.xml' % TEST_FILES_PATH

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot_citysdk_synchronizers.ProvinciaWifiCitySdkMobility'
        external._reload_schema()
        external.config = CITYSDK_MOBILITY_TEST_CONFIG.copy()
        external.config.update({
            "status": "active",
            "url": xml_url,
            "verify_ssl": False
        })
        external.full_clean()
        external.save()

        querystring_params = {
            'layer': CITYSDK_MOBILITY_TEST_CONFIG['citysdk_layer'],
            'per_page': '1000'
        }
        citysdk_nodes_url = '%s/nodes' % CITYSDK_MOBILITY_TEST_CONFIG['citysdk_url']
        data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
        self.assertEqual(len(data['results']), 0)

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('5 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('5 total external', output)
        self.assertIn('5 total local', output)
        self.assertEqual(layer.node_set.count(), 5)

        sleep(1)

        data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
        self.assertEqual(len(data['results']), 5)

        ### --- with the following step we expect some nodes to be deleted and some to be added --- ###

        external.config['url'] = '%s/provincia-wifi2.xml' % TEST_FILES_PATH
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('1 nodes added', output)
        self.assertIn('2 nodes unmodified', output)
        self.assertIn('3 nodes deleted', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('3 total external', output)
        self.assertIn('3 total local', output)
        self.assertEqual(layer.node_set.count(), 3)

        data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
        self.assertEqual(len(data['results']), 3)

        sleep(1)

        ### --- delete everything --- ###

        for node in layer.node_set.all():
            node.delete()

        sleep(1)  # wait 1 second

        data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
        self.assertEqual(len(data['results']), 0)
