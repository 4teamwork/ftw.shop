from zope.interface import implements
from zope.interface import Interface
from zope.component import adapts

from ftw.shop.interfaces import IStatusSet

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from ftw.shop import shopMessageFactory as _

class DefaultStatusSet(object):
    implements(IStatusSet)
    adapts(Interface)
    # plone.registry.interfaces.IRecordsProxy
    # ftw.shop.interfaces.IShopConfiguration
    title = u"Default Status Set"

    vocabulary = SimpleVocabulary(
        [SimpleTerm(value=1,
                    token=1,
                    title=_(u'status_online_pending',
                            default=u'Pending (online payment)'),
                    ),
         SimpleTerm(value=2,
                    token=2,
                    title=_(u'status_confirmed',
                            default=u'Confirmed (online payment)'),
                    ),
         SimpleTerm(value=3,
                    token=3,
                    title=_(u'status_on_account',
                            default=u'On account'),
                    )
          ]
        )

    def __init__(self, context):
        self.context = context
        pass
