from django.db.models import Q
from django.test import testcases

from journal.api.filters import RQLFilterBackend


class FiltersTestCase(testcases.TestCase):

    def test_parse_base_functions(self):
        parsed = RQLFilterBackend.parse_rql('and(eq(a,1),gt(b,2),lt(c,3),in(e,(4,5,6)))')

        expected = [['AND', ['exact', 'a', '1'], ['gt', 'b', '2'], ['lt', 'c', '3'], ['in', 'e', ['4', '5', '6']]]]

        assert parsed == expected

    def test_parse_nested(self):
        parsed = RQLFilterBackend.parse_rql('and(or(eq(a,1),gt(b,2)),and(lt(c,3),gt(e,4)))')

        expected = [['AND', ['OR', ['exact', 'a', '1'], ['gt', 'b', '2']], ['AND', ['lt', 'c', '3'], ['gt', 'e', '4']]]]

        assert parsed == expected

    def test_make_filters(self):
        parsed = RQLFilterBackend.parse_rql('and(eq(a,1),gt(b,2),lt(c,3),in(e,(4,5,6)))')

        filters = RQLFilterBackend.make_query(parsed)

        assert str(filters) == str([Q(a__exact=1, b__gt=2, c__lt=3, e__in=[4, 5, 6])])

    def test_make_filters_nested(self):
        parsed = RQLFilterBackend.parse_rql('and(or(eq(a,1),gt(b,2)),and(lt(c,3),gt(e,4)))')
        filters = RQLFilterBackend.make_query(parsed)

        assert str(filters) == str([(Q(a__exact=1) | Q(b__gt=2)) & Q(c__lt=3, e__gt=4)])
