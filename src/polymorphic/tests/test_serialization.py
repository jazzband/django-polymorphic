"""
Tests for serialization and dumpdata functionality.

This module tests that polymorphic models are correctly serialized using Django's
dumpdata command, both via call_command and subprocess invocation.

Regression test for issue #146 - ensuring dumpdata works correctly with polymorphic
models.
"""

import json
import os
import pytest
import tempfile
import subprocess
import sys
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.db import connections

from polymorphic.tests.models import (
    Model2A,
    Model2B,
    Model2C,
    Model2BFiltered,
    Model2CFiltered,
    RelatingModel,
    NatKeyParent,
    NatKeyChild,
)
from .utils import is_sqlite_in_memory, is_oracle, get_subprocess_test_db_env

manage_py = Path(__file__).parent.parent.parent.parent / "manage.py"
assert manage_py.exists()


def call_dumpdata(*models, natural_foreign=True, natural_primary=True, all=False):
    out = StringIO()
    call_command(
        "dumpdata",
        *models,
        format="json",
        stdout=out,
        natural_foreign=natural_foreign,
        natural_primary=natural_primary,
        all=all,
    )
    return json.loads(out.getvalue())


def run_dumpdata(*models, natural_foreign=True, natural_primary=True, all=False):
    cmd = [sys.executable, manage_py, "dumpdata", *models, "--format=json"]
    if natural_foreign:
        cmd.append("--natural-foreign")
    if all:
        cmd.append("--all")
    if natural_primary:
        cmd.append("--natural-primary")
    result = subprocess.run(cmd, capture_output=True, env=get_subprocess_test_db_env())
    assert result.returncode == 0, result.stderr or result.stdout
    return json.loads(result.stdout)


@pytest.fixture
def dump_objects(db):
    return (
        Model2A.objects.create(field1="A1"),
        Model2B.objects.create(field1="B1", field2="B2"),
        Model2C.objects.create(field1="C1", field2="C2", field3="C3"),
        Model2BFiltered.objects.create(field1="BF1", field2="BF2"),
        Model2CFiltered.objects.create(field1="cf1", field2="cf2", field3="cf3"),
        Model2CFiltered.objects.create(field1="CF1", field2="CF2", field3="CF3"),
    )


@pytest.fixture
def natkey_dump_objects(db):
    """
    Create a small graph of NatKeyParent / NatKeyChild instances.

    Returns:
        tuple[list[NatKeyParent], list[NatKeyChild]]
    """
    return [
        NatKeyChild.objects.create(slug=f"slug-{i}", content=f"content {i}", val=i)
        for i in range(5)
    ]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "dumpdata",
    [
        pytest.param(call_dumpdata, id="call_command"),
        pytest.param(
            run_dumpdata,
            id="manage",
            marks=pytest.mark.skipif(
                is_sqlite_in_memory(),
                reason="Subprocess test disabled for in-memory sqlite test runs",
            ),
        ),
    ],
)
@pytest.mark.parametrize("all", [False, True])
def test_dumpdata_returns_base_objects_not_downcasted(dumpdata, dump_objects, all):
    """
    Test that dumpdata serializes base table rows without polymorphic downcasting.

    When querying Model2A table directly, we should get 3 rows
    (A, B, C base objects).
    """
    # Should have only Model2As
    assert dumpdata("tests.Model2A", all=all) == [
        {
            "fields": {"field1": "A1", "polymorphic_ctype": ["tests", "model2a"]},
            "model": "tests.model2a",
            "pk": dump_objects[0].pk,
        },
        {
            "fields": {"field1": "B1", "polymorphic_ctype": ["tests", "model2b"]},
            "model": "tests.model2a",
            "pk": dump_objects[1].pk,
        },
        {
            "fields": {"field1": "C1", "polymorphic_ctype": ["tests", "model2c"]},
            "model": "tests.model2a",
            "pk": dump_objects[2].pk,
        },
        {
            "fields": {"field1": "BF1", "polymorphic_ctype": ["tests", "model2bfiltered"]},
            "model": "tests.model2a",
            "pk": dump_objects[3].pk,
        },
        {
            "fields": {"field1": "cf1", "polymorphic_ctype": ["tests", "model2cfiltered"]},
            "model": "tests.model2a",
            "pk": dump_objects[4].pk,
        },
        {
            "fields": {"field1": "CF1", "polymorphic_ctype": ["tests", "model2cfiltered"]},
            "model": "tests.model2a",
            "pk": dump_objects[5].pk,
        },
    ]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "dumpdata",
    [
        pytest.param(call_dumpdata, id="call_command"),
        pytest.param(
            run_dumpdata,
            id="manage",
            marks=pytest.mark.skipif(
                is_sqlite_in_memory() or is_oracle(),
                reason="Subprocess test disabled for in-memory sqlite test runs",
            ),
        ),
    ],
)
@pytest.mark.parametrize("all", [False, True], ids=["default", "all"])
def test_dumpdata_all_flag(dumpdata, dump_objects, all):
    """Test dumping only a child model works correctly."""

    expected = [
        *(
            [
                {
                    "fields": {"model2b_ptr": dump_objects[3].pk},
                    "model": "tests.model2bfiltered",
                    "pk": dump_objects[3].pk,
                }
            ]
            if all
            else []
        ),
        {
            "fields": {"model2b_ptr": dump_objects[4].pk},
            "model": "tests.model2bfiltered",
            "pk": dump_objects[4].pk,
        },
        *(
            [
                {
                    "fields": {"model2b_ptr": dump_objects[5].pk},
                    "model": "tests.model2bfiltered",
                    "pk": dump_objects[5].pk,
                }
            ]
            if all
            else []
        ),
        {
            "fields": {"field3": "cf3", "model2bfiltered_ptr": dump_objects[4].pk},
            "model": "tests.model2cfiltered",
            "pk": dump_objects[4].pk,
        },
        *(
            [
                {
                    "fields": {"field3": "CF3", "model2bfiltered_ptr": dump_objects[5].pk},
                    "model": "tests.model2cfiltered",
                    "pk": dump_objects[5].pk,
                }
            ]
            if all
            else []
        ),
    ]
    assert dumpdata("tests.Model2BFiltered", "tests.Model2CFiltered", all=all) == expected


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "dumpdata",
    [
        pytest.param(call_dumpdata, id="call_command"),
        pytest.param(
            run_dumpdata,
            id="manage",
            marks=pytest.mark.skipif(
                is_sqlite_in_memory() or is_oracle(),
                reason="Subprocess test disabled for in-memory sqlite test runs",
            ),
        ),
    ],
)
def test_dumpdata_child_model_only(dumpdata, dump_objects):
    """Test dumping only a child model works correctly."""
    assert dumpdata("tests.Model2C") == [
        {
            "fields": {
                "field3": "C3",
                "model2b_ptr": dump_objects[2].pk,
            },
            "model": "tests.model2c",
            "pk": dump_objects[2].pk,
        }
    ]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "dumpdata",
    [
        pytest.param(call_dumpdata, id="call_command"),
        pytest.param(
            run_dumpdata,
            id="manage",
            marks=pytest.mark.skipif(
                is_sqlite_in_memory() or is_oracle(),
                reason="Subprocess test disabled for in-memory sqlite test runs",
            ),
        ),
    ],
)
@pytest.mark.parametrize("all", [False, True], ids=["default", "all"])
def test_dumpdata_multi_table_roundtrip(dumpdata, dump_objects, all):
    data = dumpdata(
        "tests.Model2A",
        "tests.Model2B",
        "tests.Model2C",
        "tests.Model2BFiltered",
        "tests.Model2CFiltered",
        all=all,
    )

    # When dumping Model2A (the parent model), ALL instances are returned regardless of
    # the `all` parameter, because Model2A doesn't have a filtered manager.
    # The `all` parameter only affects behavior when dumping child models WITHOUT their parent.
    expected = [
        {
            "fields": {"field1": "A1", "polymorphic_ctype": ["tests", "model2a"]},
            "model": "tests.model2a",
            "pk": dump_objects[0].pk,
        },
        {
            "fields": {"field1": "B1", "polymorphic_ctype": ["tests", "model2b"]},
            "model": "tests.model2a",
            "pk": dump_objects[1].pk,
        },
        {
            "fields": {"field1": "C1", "polymorphic_ctype": ["tests", "model2c"]},
            "model": "tests.model2a",
            "pk": dump_objects[2].pk,
        },
        {
            "fields": {"field1": "BF1", "polymorphic_ctype": ["tests", "model2bfiltered"]},
            "model": "tests.model2a",
            "pk": dump_objects[3].pk,
        },
        {
            "fields": {"field1": "cf1", "polymorphic_ctype": ["tests", "model2cfiltered"]},
            "model": "tests.model2a",
            "pk": dump_objects[4].pk,
        },
        {
            "fields": {"field1": "CF1", "polymorphic_ctype": ["tests", "model2cfiltered"]},
            "model": "tests.model2a",
            "pk": dump_objects[5].pk,
        },
        {
            "fields": {"field2": "B2", "model2a_ptr": dump_objects[1].pk},
            "model": "tests.model2b",
            "pk": dump_objects[1].pk,
        },
        {
            "fields": {"field2": "C2", "model2a_ptr": dump_objects[2].pk},
            "model": "tests.model2b",
            "pk": dump_objects[2].pk,
        },
        {
            "fields": {"field2": "BF2", "model2a_ptr": dump_objects[3].pk},
            "model": "tests.model2b",
            "pk": dump_objects[3].pk,
        },
        {
            "fields": {"field2": "cf2", "model2a_ptr": dump_objects[4].pk},
            "model": "tests.model2b",
            "pk": dump_objects[4].pk,
        },
        {
            "fields": {"field2": "CF2", "model2a_ptr": dump_objects[5].pk},
            "model": "tests.model2b",
            "pk": dump_objects[5].pk,
        },
        {
            "fields": {"field3": "C3", "model2b_ptr": dump_objects[2].pk},
            "model": "tests.model2c",
            "pk": dump_objects[2].pk,
        },
        *(
            [
                {
                    "fields": {"model2b_ptr": dump_objects[3].pk},
                    "model": "tests.model2bfiltered",
                    "pk": dump_objects[3].pk,
                }
            ]
            if all
            else []
        ),
        {
            "fields": {"model2b_ptr": dump_objects[4].pk},
            "model": "tests.model2bfiltered",
            "pk": dump_objects[4].pk,
        },
        *(
            [
                {
                    "fields": {"model2b_ptr": dump_objects[5].pk},
                    "model": "tests.model2bfiltered",
                    "pk": dump_objects[5].pk,
                }
            ]
            if all
            else []
        ),
        {
            "fields": {"field3": "cf3", "model2bfiltered_ptr": dump_objects[4].pk},
            "model": "tests.model2cfiltered",
            "pk": dump_objects[4].pk,
        },
        *(
            [
                {
                    "fields": {"field3": "CF3", "model2bfiltered_ptr": dump_objects[5].pk},
                    "model": "tests.model2cfiltered",
                    "pk": dump_objects[5].pk,
                }
            ]
            if all
            else []
        ),
    ]

    assert data == expected

    Model2A.objects.all().delete()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(json.dumps(data))
        fixture_file = f.name

    try:
        call_command("loaddata", fixture_file, verbosity=0)

        # After loaddata, all 6 objects are loaded
        assert Model2A.objects.count() == 6
        assert Model2B.objects.count() == 5
        assert Model2C.objects.count() == 1
        # Filtered managers still apply, so only cf1 passes the filter
        assert Model2BFiltered.objects.count() == 1
        assert Model2CFiltered.objects.count() == 1

        model2a_objects = list(Model2A.objects.order_by("pk"))
        a, b, c, bf, cf_lower, cf_upper = model2a_objects

        assert a.__class__ == Model2A
        assert b.__class__ == Model2B
        assert c.__class__ == Model2C
        assert cf_lower.__class__ == Model2CFiltered

        if all:
            assert bf.__class__ == Model2BFiltered
            assert cf_upper.__class__ == Model2CFiltered
        else:
            # the parent class wasnt filtered so these should have been upcasted
            assert bf.__class__ == Model2B
            assert cf_upper.__class__ == Model2B

        assert a.field1 == "A1"
        assert b.field1 == "B1"
        assert b.field2 == "B2"
        assert c.field1 == "C1"
        assert c.field2 == "C2"
        assert c.field3 == "C3"
        assert cf_lower.field1 == "cf1"
        assert cf_lower.field2 == "cf2"
        assert cf_lower.field3 == "cf3"

        if all:
            assert bf.field1 == "BF1"
            assert bf.field2 == "BF2"
            assert cf_upper.field1 == "CF1"
            assert cf_upper.field2 == "CF2"
            assert cf_upper.field3 == "CF3"
        else:
            assert bf.field1 == "BF1"
            assert bf.field2 == "BF2"
            # cf_upper is now a Model2B, so field3 does not exist
            assert cf_upper.field1 == "CF1"
            assert cf_upper.field2 == "CF2"
            assert not hasattr(cf_upper, "field3")

    finally:
        # Clean up temporary file
        os.unlink(fixture_file)


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "dumpdata",
    [
        pytest.param(call_dumpdata, id="call_command"),
        pytest.param(
            run_dumpdata,
            id="manage",
            marks=pytest.mark.skipif(
                is_sqlite_in_memory() or is_oracle(),
                reason="Subprocess test disabled for in-memory sqlite test runs",
            ),
        ),
    ],
)
@pytest.mark.parametrize("all", [False, True], ids=["default", "all"])
def test_dumpdata_related_polymorphic_roundtrip(dumpdata, dump_objects, all):
    rm1 = RelatingModel.objects.create()
    rm2 = RelatingModel.objects.create()
    rm3 = RelatingModel.objects.create()
    rm1.many2many.add(dump_objects[0])
    rm2.many2many.add(dump_objects[1], dump_objects[2])
    # Add all filtered models to rm3
    rm3.many2many.add(dump_objects[3], dump_objects[4], dump_objects[5])

    data = dumpdata(
        "tests.Model2A",
        "tests.Model2B",
        "tests.Model2C",
        "tests.Model2BFiltered",
        "tests.Model2CFiltered",
        "tests.RelatingModel",
        natural_foreign=True,
        natural_primary=False,
        all=all,
    )

    Model2A.objects.all().delete()
    RelatingModel.objects.all().delete()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(json.dumps(data))
        fixture_file = f.name

    try:
        call_command("loaddata", fixture_file, verbosity=0)

        # After loaddata, all 6 objects are loaded
        assert Model2A.objects.count() == 6
        assert Model2B.objects.count() == 5
        assert Model2C.objects.count() == 1
        # Filtered managers still apply, so only cf1 passes the filter
        assert Model2BFiltered.objects.count() == 1
        assert Model2BFiltered._base_manager.count() == (3 if all else 1)
        assert Model2CFiltered.objects.count() == 1
        assert Model2CFiltered._base_manager.count() == (2 if all else 1)

        model2a_objects = Model2A.objects.order_by("pk")
        a, b, c, bf, cf_lower, cf_upper = model2a_objects.all()

        assert a.__class__ == Model2A
        assert b.__class__ == Model2B
        assert c.__class__ == Model2C
        assert cf_lower.__class__ == Model2CFiltered

        if all:
            assert bf.__class__ == Model2BFiltered
            assert cf_upper.__class__ == Model2CFiltered
        else:
            # the parent class wasnt filtered so these should have been upcasted
            assert bf.__class__ == Model2B
            assert cf_upper.__class__ == Model2B

        assert a.field1 == "A1"
        assert b.field1 == "B1"
        assert b.field2 == "B2"
        assert c.field1 == "C1"
        assert c.field2 == "C2"
        assert c.field3 == "C3"
        assert cf_lower.field1 == "cf1"
        assert cf_lower.field2 == "cf2"
        assert cf_lower.field3 == "cf3"

        if all:
            assert bf.field1 == "BF1"
            assert bf.field2 == "BF2"
            assert cf_upper.field1 == "CF1"
            assert cf_upper.field2 == "CF2"
            assert cf_upper.field3 == "CF3"
        else:
            assert bf.field1 == "BF1"
            assert bf.field2 == "BF2"
            # cf_upper is now a Model2B, so field3 does not exist
            assert cf_upper.field1 == "CF1"
            assert cf_upper.field2 == "CF2"
            assert not hasattr(cf_upper, "field3")

        # Verify relationships
        assert RelatingModel.objects.count() == 3
        rm_objects = list(RelatingModel.objects.order_by("pk"))

        # rm1 has A
        assert rm_objects[0].many2many.count() == 1
        assert rm_objects[0].many2many.first() == a

        # rm2 has B and C
        assert rm_objects[1].many2many.count() == 2
        assert set(rm_objects[1].many2many.all()) == {b, c}

        # rm3 has all three filtered models
        assert rm_objects[2].many2many.count() == 3
        rm3_related = set(rm_objects[2].many2many.all())
        assert len(rm3_related) == 3
        assert bf in rm3_related
        assert cf_lower in rm3_related
        assert cf_upper in rm3_related

    finally:
        # Clean up temporary file
        os.unlink(fixture_file)


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "dumpdata",
    [
        pytest.param(call_dumpdata, id="call_command"),
        pytest.param(
            run_dumpdata,
            id="manage",
            marks=pytest.mark.skipif(
                is_sqlite_in_memory() or is_oracle(),
                reason="Subprocess test disabled for in-memory sqlite test runs",
            ),
        ),
    ],
)
def test_dumpdata_natural_keys(dumpdata, natkey_dump_objects):
    data = dumpdata(
        "tests",
        natural_foreign=True,
        natural_primary=True,
        all=all,
    )

    assert data == [
        {
            "fields": {
                "content": "content 0",
                "polymorphic_ctype": ["tests", "natkeychild"],
                "slug": "slug-0",
            },
            "model": "tests.natkeyparent",
        },
        {
            "fields": {
                "content": "content 1",
                "polymorphic_ctype": ["tests", "natkeychild"],
                "slug": "slug-1",
            },
            "model": "tests.natkeyparent",
        },
        {
            "fields": {
                "content": "content 2",
                "polymorphic_ctype": ["tests", "natkeychild"],
                "slug": "slug-2",
            },
            "model": "tests.natkeyparent",
        },
        {
            "fields": {
                "content": "content 3",
                "polymorphic_ctype": ["tests", "natkeychild"],
                "slug": "slug-3",
            },
            "model": "tests.natkeyparent",
        },
        {
            "fields": {
                "content": "content 4",
                "polymorphic_ctype": ["tests", "natkeychild"],
                "slug": "slug-4",
            },
            "model": "tests.natkeyparent",
        },
        {"fields": {"foo": ["slug-0"], "val": 0}, "model": "tests.natkeychild"},
        {"fields": {"foo": ["slug-1"], "val": 1}, "model": "tests.natkeychild"},
        {"fields": {"foo": ["slug-2"], "val": 2}, "model": "tests.natkeychild"},
        {"fields": {"foo": ["slug-3"], "val": 3}, "model": "tests.natkeychild"},
        {"fields": {"foo": ["slug-4"], "val": 4}, "model": "tests.natkeychild"},
    ]

    NatKeyChild.objects.all().delete()
    NatKeyParent.objects.all().delete()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(json.dumps(data))
        fixture_file = f.name

    try:
        call_command("loaddata", fixture_file, verbosity=0)

        for old, new in zip(
            natkey_dump_objects,
            NatKeyParent.objects.order_by("pk").all(),
        ):
            assert new.__class__ == old.__class__ is NatKeyChild
            assert new.slug == old.slug
            assert new.content == old.content
            assert new.val == old.val

    finally:
        # Clean up temporary file
        os.unlink(fixture_file)
