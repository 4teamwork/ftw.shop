from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getAdapters
from zope.interface import directlyProvides

from ftw.shop.interfaces import IContactInformationStep

def ContactInfoSteps(context):
    # context is the portal config options, whose context is the portal
    contact_info_steps = getAdapters((context, None, context,), IContactInformationStep)
    step_names = set( map(unicode, [ n for n,a in contact_info_steps]) )
    directlyProvides(ContactInfoSteps, IVocabularyFactory)
    return vocabulary.SimpleVocabulary.fromValues(step_names)