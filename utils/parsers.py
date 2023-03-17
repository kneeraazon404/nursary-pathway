from collections import OrderedDict

from django.http.request import QueryDict
from djangorestframework_camel_case.parser import CamelCaseMultiPartParser
from drf_nested_forms.settings import api_settings as drf_nested_forms_api_settings
from drf_nested_forms.utils import NestedForm


class NestedCamelCaseMultiPartParser(CamelCaseMultiPartParser):
    options = drf_nested_forms_api_settings.OPTIONS

    def parse(self, stream, media_type, parser_context):
        parsed = super().parse(stream, media_type, parser_context)
        if parsed.files:
            self._full_data = parsed.data.copy()
            self._full_data.update(parsed.files)
        else:
            self._full_data = parsed.data
        self._ordered_data = QueryDict("", mutable=True)
        ordered_data = dict(
            OrderedDict(
                sorted(self._full_data.items(), key=lambda t: (len(t[0]), t[0]))
            )
        )
        self._ordered_data.update(ordered_data)

        form = NestedForm(self._ordered_data, **self.options)

        if form.is_nested():
            return form.data
        return parsed
