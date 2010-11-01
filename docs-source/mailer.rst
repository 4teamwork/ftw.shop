:mod:`mailer` --- MailHost abstraction for Plone 3 backwards compatiblity
=========================================================================

.. automodule:: mailer
      :members:
      :undoc-members:


Example usage
-------------

.. code-block:: python

	from email.Utils import formataddr
	from ftw.shop.interfaces import IMailHostAdapter

	mailTo = formataddr(('John Doe', 'john.doe@example.org'))
	mailFrom = 'webshop@example.org'
	mailSubject = getattr('Test Subject')
	msg_body = """Dear Mr. Doe, ..."""
		
	mhost = IMailHostAdapter(self.context)
	mhost.send(msg_body,
	             mto=mailTo,
	             mfrom=mailFrom,
	             mbcc=mailBcc,
	             subject=mailSubject,
	             encode=None,
	             immediate=False,
	             msg_type='text/plain',
	             charset='utf8')

