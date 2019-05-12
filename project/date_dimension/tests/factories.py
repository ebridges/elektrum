from datetime import date, datetime, timezone

import pytest
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDate
from pytest_factoryboy import register

from date_dimension.models import DateDimension


class DateDimensionFactory(DjangoModelFactory):
    class Meta:
        model = DateDimension

    from_date = FuzzyDate(start_date=date(2010, 2, 26)).fuzz()

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        return model_class.create_from(*args, **kwargs)


register(DateDimensionFactory)
