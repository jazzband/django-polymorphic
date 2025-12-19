from _typeshed import Incomplete
from django.template import Node

register: Incomplete

class BreadcrumbScope(Node):
    base_opts: Incomplete
    nodelist: Incomplete
    def __init__(self, base_opts, nodelist) -> None: ...
    @classmethod
    def parse(cls, parser, token): ...
    def render(self, context): ...

@register.tag
def breadcrumb_scope(parser, token): ...
