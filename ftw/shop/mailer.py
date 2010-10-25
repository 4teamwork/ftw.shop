import logging
import socket

from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface
from Products.MailHost.MailHost import MailHostError
from email import message_from_string
from email.Header import Header
from email.Utils import formataddr

from ftw.shop.interfaces import IMailHostAdapter

logger  = logging.getLogger('ftw.shop')


class MailHostAdapter(object):
    """Abstracts a MailHost and handles slightly different implementations
    in Plone 4 and Plone <= 3.
    """
    implements(IMailHostAdapter)
    adapts(Interface)

    def __init__(self, context):
        self.context = context

    def send(self, msg_body, mto=None, mfrom=None, mbcc=None, subject=None, 
             encode=None, immediate=False, charset=None, msg_type=None):
        """Send mail.
        """
        mhost = self.context.MailHost
        
        # msg can be the message with or without headers, or an
        # email.Message.Message object 
        msg_body
        
        msg = message_from_string(msg_body.encode(charset))
        msg.set_charset(charset)
        msg['BCC']= Header(mbcc)

        subtype = msg_type.split('/')[1]

        try:
            # Plone 4
            msg.set_charset(charset)
            mhost.send(msg,
                         mto=mto,
                         mfrom=mfrom,
                         subject=subject,
                         encode=encode,
                         immediate=immediate,
                         msg_type=msg_type,
                         charset=charset)
        except TypeError:
            # Plone 3 or earlier
            mhost.secureSend(msg_body,
                             mto=mto,
                             mfrom=mfrom,
                             subject=subject,
                             mbcc=mbcc,
                             subtype=subtype,
                             charset=charset)
            
        except (MailHostError, socket.error), e:
            logger.error("sending mail with subject %s to %s failed: %s." 
                         % (subject, mto ,str(e)))
        return
