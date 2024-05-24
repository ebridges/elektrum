from datetime import date
from uuid import uuid4

import pytest

from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText
from factory import LazyFunction, SubFactory, post_generation
from pytest_factoryboy import register

from sharing.models import Audience, Share, ShareState
from users.tests.factories import UserFactory
from date_dimension.tests.factories import DateDimensionFactory
from media_items.tests.factories import MediaItemFactory


@pytest.fixture
def share_populated(custom_user, count_shared=5, count_shared_to=5):
    date_dimension = DateDimensionFactory(from_date=date(1950, 9, 11))
    media_items = MediaItemFactory.create_batch(
        size=count_shared, owner=custom_user, create_day=date_dimension
    )
    audiences = AudienceFactory.create_batch(size=count_shared_to, shared_by=custom_user)
    return ShareFactory(shared_by=custom_user, shared_to=audiences, shared=media_items)


class AudienceFactory(DjangoModelFactory):
    class Meta:
        model = Audience

    id = LazyFunction(uuid4)
    email = FuzzyText(prefix='audience@', suffix='.com')
    shared_by = SubFactory(UserFactory)
    unsubscribed = False


class ShareFactory(DjangoModelFactory):
    class Meta:
        model = Share
        # DeprecationWarning: ShareFactory._after_postgeneration 
        # will stop saving the instance after postgeneration hooks 
        # in the next major release.
        # - If the save call is extraneous, set 
        #   `skip_postgeneration_save=True`` in the ShareFactory.Meta. 
        # - To keep saving the instance, move the save call to your 
        #   postgeneration hooks or override _after_postgeneration.
        skip_postgeneration_save=True

    id = LazyFunction(uuid4)
    subject = FuzzyText(prefix='subject.')
    message = FuzzyText(prefix='message.')
    shared_by = SubFactory(UserFactory)

    @post_generation
    def shared_to(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for audience in extracted:
                audience.shared_by = self.shared_by
                self.shared_to.add(audience)

    @post_generation
    def shared(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for media_item in extracted:
                self.shared.add(media_item)


register(AudienceFactory)
register(ShareFactory)
