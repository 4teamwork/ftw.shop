import logging
import socket

from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface
from Products.MailHost.MailHost import MailHostError
from email import message_from_string
from email.Header import Header

try:
    from email.encoders import encode_quopri, encode_base64
except ImportError:
    # Python 2.4, and therefore Plone < 4
    pass

from ftw.shop.interfaces import IMailHostAdapter

logger = logging.getLogger('ftw.shop')


class MailHostAdapter(object):
    """Abstracts a MailHost and handles slightly different implementations
    in Plone 4 and Plone <= 3.
    """
    implements(IMailHostAdapter)
    adapts(Interface)

    def __init__(self, context):
        self.context = context

    def send(self, msg_body, mto, mfrom=None, mbcc=None, reply_to=None, subject=None,
             encode=None, immediate=False, charset=None, msg_type=None):
        """Sends a message defined at least by its message body and the
        destination address.
        """
        mhost = self.context.MailHost

        try:
            # Plone 4
            msg = message_from_string(msg_body.encode(charset))
            if encode is None or encode in ["quoted-printable", "qp"]:
                encode_quopri(msg)
            else:
                encode_base64(msg)

            msg['BCC']= Header(mbcc)
            if reply_to:
                msg['Reply-To'] = Header(reply_to)

            mhost.send(msg,
                         mto=mto,
                         mfrom=mfrom,
                         subject=subject,
                         encode=encode,
                         immediate=immediate,
                         msg_type=msg_type,
                         charset=charset)
        except (TypeError, NameError):
            # Plone 3 or earlier
            subtype = msg_type.split('/')[1]

            mhost.secureSend(msg_body,
                             mto=mto,
                             mfrom=mfrom,
                             subject=subject,
                             mbcc=mbcc,
                             subtype=subtype,
                             charset=charset)

        except (MailHostError, socket.error), e:
            logger.error("sending mail with subject %s to %s failed: %s."
                         % (subject, mto, str(e)))
        return
