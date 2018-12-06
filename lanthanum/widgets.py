import copy
import json

from django_admin_json_editor import JSONEditorWidget
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class JSONEditorWidget(JSONEditorWidget):
    template_name = 'lanthanum/_json_editor_widget.html'

    def render(self, name, value, attrs=None, renderer=None):
        """
        Fix the JSON Editor widget by doing a standard json dump for dict data

        This will not convert booleans to ints like the standard JSON Editor.
        """
        if callable(self._schema):
            schema = self._schema(self)
        else:
            schema = copy.copy(self._schema)

        schema['title'] = ' '
        schema['options'] = {'collapsed': int(self._collapsed)}

        context = {
            'name': name,
            'schema': json.dumps(schema),
            'data': value,
            'sceditor': int(self._sceditor),
        }
        return mark_safe(render_to_string(self.template_name, context))
