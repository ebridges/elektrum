from uuid import uuid4

from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText
from factory import LazyFunction, SubFactory, post_generation
from pytest_factoryboy import register

from sharing.models import Audience, Share
from users.tests.factories import UserFactory


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
