from _typeshed import Incomplete
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from polymorphic import tests as tests
from polymorphic.admin import (
    PolymorphicChildModelAdmin as PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter as PolymorphicChildModelFilter,
    PolymorphicInlineSupportMixin as PolymorphicInlineSupportMixin,
    PolymorphicParentModelAdmin as PolymorphicParentModelAdmin,
    StackedPolymorphicInline as StackedPolymorphicInline,
)
from polymorphic.tests.admintestcase import AdminTestCase as AdminTestCase
from polymorphic.tests.models import (
    InlineModelA as InlineModelA,
    InlineModelB as InlineModelB,
    InlineParent as InlineParent,
    Model2A as Model2A,
    Model2B as Model2B,
    Model2C as Model2C,
    Model2D as Model2D,
    NoChildren as NoChildren,
    PlainA as PlainA,
)
from time import sleep as sleep

class PolymorphicAdminTests(AdminTestCase):
    def test_admin_registration(self): ...
    def test_get_child_inlines(self) -> None: ...
    def test_admin_inlines(self) -> None: ...

class _GenericAdminFormTest(StaticLiveServerTestCase):
    HEADLESS: Incomplete
    admin_username: str
    admin_password: str
    admin: Incomplete
    def admin_url(self): ...
    def add_url(self, model): ...
    def change_url(self, model, id): ...
    def list_url(self, model): ...
    def get_object_ids(self, model): ...
    @classmethod
    def setUpClass(cls) -> None: ...
    @classmethod
    def tearDownClass(cls) -> None: ...
    page: Incomplete
    def setUp(self) -> None: ...
    def tearDown(self) -> None: ...

class StackedInlineTests(_GenericAdminFormTest):
    def test_admin_inline_add_autocomplete(self) -> None: ...
    def test_inline_form_ordering_and_removal(self) -> None: ...

class PolymorphicFormTests(_GenericAdminFormTest):
    def test_admin_polymorphic_add(self) -> None: ...

class PolymorphicNoChildrenTests(_GenericAdminFormTest):
    def test_admin_no_polymorphic_children(self) -> None: ...

class AdminRecentActionsTests(_GenericAdminFormTest):
    def test_admin_recent_actions(self) -> None: ...
