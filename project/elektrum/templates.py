from jinja2.environment import Environment

from base.views.utils import DEFAULT_THUMBNAIL_H, DEFAULT_THUMBNAIL_W


class ElektrumEnvironment(Environment):
    def __init__(self, **kwargs):
        super(ElektrumEnvironment, self).__init__(**kwargs)
        self.globals['thumbnail_width'] = DEFAULT_THUMBNAIL_W
        self.globals['thumbnail_height'] = DEFAULT_THUMBNAIL_H
