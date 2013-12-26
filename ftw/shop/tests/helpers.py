import email.header
import operator


def get_mail_header(msg, name):
    return map(operator.itemgetter(0), email.header.decode_header(msg.get(name)))
