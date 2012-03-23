# -*- coding: utf8 -*-
'''
Created on 11.03.2012

@author: rklain
'''
from wtforms.fields.core import Field
from wtforms.widgets.core import TextInput
import logging

log = logging.getLogger(__name__)

#===============================================================================
# TagField
#===============================================================================
class TagField(Field):
    widget = TextInput()

    def __init__(self, label='', validators=None, separator=',', remove_duplicates=True, **kwargs):
        super(TagField, self).__init__(label, validators, **kwargs)
        self.separator = separator
        self.remove_duplicates = remove_duplicates

    def _value(self):
        ''' is called by the TextInput widget to provide the value that is displayed '''
        if self.data:
            log.debug(self.data)
            # TODO: separate tag list imput from our model?
            return unicode((self.separator + ' ').join([nodetag.tag.name for nodetag in self.data]))
        else:
            return u''

    def process_formdata(self, valuelist):
        '''
        process_formdata processes the incoming data back into a list of tags
        '''
        if valuelist:
            self.data = [x.strip().lower() for x in valuelist[0].split(self.separator)]
        else:
            self.data = []
        if self.remove_duplicates:
            self.data = list(self._remove_duplicates(self.data))

    @classmethod
    def _remove_duplicates(cls, seq):
        d = {}
        for item in seq:
            if item.lower() not in d:
                d[item.lower()] = True
                yield item
