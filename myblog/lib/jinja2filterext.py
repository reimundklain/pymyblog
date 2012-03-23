import logging
import markdown

log = logging.getLogger(__name__)

def markup(value, *args, **kwargs):
    kwargs['output_format'] = 'xhtml1'
    return markdown.markdown(value, *args, **kwargs)
