from uuid import uuid4

from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyNaiveDateTime, FuzzyText
from factory import (
    Sequence,
    SubFactory,
    LazyAttribute,
    SelfAttribute,
    LazyFunction,
    post_generation,
)
from pytest_factoryboy import register

from sharing.models import Audience, Share, AudienceShare, ShareState
from users.tests.factories import UserFactory
from media_items.tests.factories import MediaItemFactory


class ShareFactory(DjangoModelFactory):
    class Meta:
        model = Share

    id = LazyFunction(uuid4)
    subject = FuzzyText(prefix='subject.')
    message = FuzzyText(prefix='message.')

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


register(ShareFactory)
