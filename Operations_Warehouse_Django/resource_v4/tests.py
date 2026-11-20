from unittest import mock

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIRequestFactory

from resource_v4.views import Resource_GSearch


class GSearchParsingTests(SimpleTestCase):
    def test_sort_defaults_to_asc(self):
        self.assertEqual(
            Resource_GSearch._parse_sort('title'),
            [{'field_name': 'title', 'order': 'asc'}])

    def test_sort_multiple_with_orders(self):
        self.assertEqual(
            Resource_GSearch._parse_sort('title:asc, type:DESC'),
            [{'field_name': 'title', 'order': 'asc'},
             {'field_name': 'type', 'order': 'desc'}])

    def test_sort_invalid_order(self):
        with self.assertRaises(ValueError):
            Resource_GSearch._parse_sort('title:up')

    def test_sort_missing_field(self):
        with self.assertRaises(ValueError):
            Resource_GSearch._parse_sort(':desc')

    def test_facets_become_terms_facets(self):
        self.assertEqual(
            Resource_GSearch._parse_facets('type, organization,'),
            [{'name': 'type', 'type': 'terms', 'field_name': 'type'},
             {'name': 'organization', 'type': 'terms', 'field_name': 'organization'}])


@override_settings(GLOBUS_CLIENT_ID='id', GLOBUS_CLIENT_SECRET='secret',
                   GLOBUS_SEARCH_INDEX_ID='index')
class GSearchViewTests(SimpleTestCase):
    def setUp(self):
        patcher = mock.patch('resource_v4.views.globus_sdk')
        self.globus = patcher.start()
        self.addCleanup(patcher.stop)
        self.globus.GlobusAPIError = type('GlobusAPIError', (Exception,), {})
        self.globus.GlobusError = type('GlobusError', (Exception,), {})
        self.search_client = self.globus.SearchClient.return_value
        self.search_client.post_search.return_value.data = {'gmeta': []}

    def get(self, query):
        request = APIRequestFactory().get('/resource/v4/resource_gsearch/' + query)
        return Resource_GSearch.as_view()(request)

    def test_sort_and_facets_converted(self):
        response = self.get('?q=gpu&sort=title:desc&facets=type')
        self.assertEqual(response.status_code, 200)
        kwargs = self.globus.SearchQueryV1.call_args.kwargs
        self.assertEqual(kwargs['q'], 'gpu')
        self.assertEqual(kwargs['sort'], [{'field_name': 'title', 'order': 'desc'}])
        self.assertEqual(kwargs['facets'],
                         [{'name': 'type', 'type': 'terms', 'field_name': 'type'}])

    def test_filters_rejected(self):
        response = self.get('?filters=[]')
        self.assertEqual(response.status_code, 400)
        self.assertIn('filters', response.data['error'])

    def test_bad_sort_returns_400(self):
        response = self.get('?sort=title:sideways')
        self.assertEqual(response.status_code, 400)
        self.search_client.post_search.assert_not_called()
