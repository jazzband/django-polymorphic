from django.template import Context, Library, Node, NodeList, TemplateSyntaxError
from django.template.base import FilterExpression, Parser, Token
from typing_extensions import Self

register: Library = Library()


class BreadcrumbScope(Node):
    base_opts: FilterExpression
    nodelist: NodeList

    def __init__(self, base_opts: FilterExpression, nodelist: NodeList) -> None:
        self.base_opts = base_opts
        self.nodelist = nodelist  # Note, takes advantage of Node.child_nodelists

    @classmethod
    def parse(cls, parser: Parser, token: Token) -> Self:
        bits = token.split_contents()
        if len(bits) == 2:
            (_tagname, base_opts_str) = bits
            base_opts = parser.compile_filter(base_opts_str)
            nodelist = parser.parse(("endbreadcrumb_scope",))
            parser.delete_first_token()

            return cls(base_opts=base_opts, nodelist=nodelist)
        else:
            raise TemplateSyntaxError(f"{token.contents[0]} tag expects 1 argument")

    def render(self, context: Context) -> str:
        # app_label is really hard to overwrite in the standard Django ModelAdmin.
        # To insert it in the template, the entire render_change_form() and delete_view() have to copied and adjusted.
        # Instead, have an assignment tag that inserts that in the template.
        base_opts = self.base_opts.resolve(context)
        new_vars = {}
        if base_opts and not isinstance(base_opts, str):
            new_vars = {
                "app_label": base_opts.app_label,  # What this is all about
                "opts": base_opts,
            }

        new_scope = context.push()
        new_scope.update(new_vars)
        html = self.nodelist.render(context)
        context.pop()
        return html


@register.tag
def breadcrumb_scope(parser: Parser, token: Token) -> BreadcrumbScope:
    """
    .. templatetag:: breadcrumb_scope

    Easily allow the breadcrumb to be generated in the admin change templates.

    The ``{% breadcrumb_scope ... %}`` tag makes sure the ``{{ opts }}`` and
    ``{{ app_label }}`` values are temporary based on the provided
    ``{{ base_opts }}``.

    This allows fixing the breadcrumb in admin templates:

    .. code-block:: html+django

        {% extends "admin/change_form.html" %}
        {% load polymorphic_admin_tags %}

        {% block breadcrumbs %}
        {% breadcrumb_scope base_opts %}{{ block.super }}{% endbreadcrumb_scope %}
        {% endblock %}
    """
    return BreadcrumbScope.parse(parser, token)
