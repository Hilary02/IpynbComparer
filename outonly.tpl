
{% extends 'display_priority.tpl' %}
{%- block header -%}
SUBMIT
{% endblock header %}

{% block in_prompt %}
{%- endblock in_prompt %}

{% block output_prompt %}
{%- endblock output_prompt %}

{%- block input %}
{% endblock input %}

{% block error %}
{% endblock error %}

{% block traceback_line %}
{{ line | indent | strip_ansi }}
{% endblock traceback_line %}

{% block execute_result %}
{% block data_priority scoped %}
{{ super() }}
{%- endblock %}
{%- endblock execute_result%}

{% block stream %}
OUTPUT```
{{output.text}}
```
{% endblock stream %}

{% block data_text scoped %}
OUTPUT```
{{ output.data['text/plain']  }}
```
{% endblock data_text %}

{% block markdowncell scoped %}
{%- if "課題" in cell.source.split("\n")[0] -%}
BLOCK
{{cell.source.split("\n")[0]}}
{% endif %}
{%- endblock markdowncell %}



{% block data_html scoped %}
{{ output.data['text/html'] }}
{% endblock data_html %}

{% block data_markdown scoped %}
{{ output.data['text/markdown'] }}
{% endblock data_markdown %}

{% block unknowncell scoped %}
unknown type  {{ cell.type }}
{% endblock unknowncell %}
            