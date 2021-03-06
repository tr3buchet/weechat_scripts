# -*- coding: utf-8 -*-
"""
Author: Trey Morris <trey@treymorris.com>
Homepage: http://github.com/tr3buchet/weechat_plugins
Version: 1.0

License
------------
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


Description
------------
This plugin is for using sendmail to send notifications


Options
------------
    plugins.var.python.sendmail_notify.sendmail_location

        The sendmail executable.
        Default: /usr/sbin/sendmail

    plugins.var.python.sendmail_notify.from

        The email address the message will be from.
        NOTE: some providers override this: ex gmail
        Default: ''

    plugins.var.python.sendmail_notify.to

        The email addres the message will be sent to.
        Default: ''
"""

import weechat
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

# register script
weechat.register('sendmail_notify', 'Trey Morris', '1.0',
                 'GPL3',
                 'sendmail_notify: send notifications using sendmail',
                 '', '')

# config setup
config = {
    'sendmail_location': '/usr/sbin/sendmail',
    'to': '',
    'from': '',
    'debug': 'off',
    'only_when_away': 'on',
    'enabled': 'on',
}

for option, default_value in config.iteritems():
    config_value = weechat.config_get_plugin(option)
    if config_value:
        # value is set in weechat config, store it here
        config[option] = config_value
    else:
        # value isn't set in weechat config, set config value from defaults
        weechat.config_set_plugin(option, default_value)

    # warn if value isn't valid
    if not config[option]:
        weechat.prnt('', 'sendmail_notify:i please set option |%s|' % option)


# setup hooks
weechat.hook_print('', '', '', 1, 'send_message', '')
weechat.hook_config('plugins.var.python.sendmail_notify.*',
                    'update_config', '')


def debug_msg(msg):
    if config['debug'] == 'on':
        weechat.prnt('', 'sendmail_notify: ' + msg)


def is_ping(buffer_type, prefix, channel, highlight):
    """Determine if a message was a ping
       private type AND prefix nick is channel name = ping
       channel type AND highlight = ping
       anything else != ping
    """
    if buffer_type == 'private' and channel == prefix:
        return True
    if buffer_type == 'channel' and highlight == '1':
        return True
    return False


def send_message(data, msg_buffer, date, tags,
                 displayed, highlight, prefix, message):
    """Callback called when highlight or private message is received.
       Creates an email and uses subprocess to call sendmail to send it.

       args:
           data: appears to always be empty
           msg_buffer: an id of the buffer message was printed on
           date: date timestamp
           tags: contains tags about the message
           displayed: '1' means yes, '0' means no
           highlight: '1' if it's a highlighted messagea, '0' otherwise
           prefix: for normal messages, the nick of the sender
           message: the text portion of what the sender sent

    """
    # return if not enabled
    if not config['enabled'] == 'on':
        return weechat.WEECHAT_RC_OK

    # return if message not displayed
    if displayed == '0':
        return weechat.WEECHAT_RC_OK

    # query for extra data
    server = weechat.buffer_get_string(msg_buffer, 'localvar_server')
    channel = weechat.buffer_get_string(msg_buffer, 'localvar_channel')
    #nick = weechat.buffer_get_string(msg_buffer, 'localvar_nick')
    away_msg = weechat.buffer_get_string(msg_buffer, 'localvar_away')
    buffer_type = weechat.buffer_get_string(msg_buffer, 'localvar_type')

    # return if only_when_away is on and we aren't away
    if config['only_when_away'] == 'on':
        if not away_msg:
            # away message is empty, this means we are not away
            debug_msg('not away, not sending message')
            return weechat.WEECHAT_RC_OK

    # return unless this was a ping of some sort
    if not is_ping(buffer_type, prefix, channel, highlight):
        debug_msg('not a a ping, not sending message')
        return weechat.WEECHAT_RC_OK

    # create message body/subject
    if buffer_type == 'private':
        body = '%s: %s' % (prefix, message)
        subject = 'private message from %s on %s' % (prefix, server)
    elif buffer_type == 'channel':
        body = '%s: %s' % (prefix, message)
        subject = 'pinged in %s.%s' % (server, channel)

    # send mail
    msg = MIMEText(body)
    msg['From'] = config['from']
    msg['To'] = config['to']
    msg['Subject'] = subject
    p = Popen(['/usr/sbin/sendmail', '-t'], stdin=PIPE)
    p.communicate(msg.as_string())

    debug_msg('sent |%s|%s|%s|%s|' % (config['from'], config['to'],
                                      subject, body))
    return weechat.WEECHAT_RC_OK


def update_config(data, option, value):
    """Callback called when a script option is changed.
       Stores the config value so it can be retrieved locally when sending
       messages. (may be an unnecessary optimization)
    """

    option = option.split('.')[-1]
    config[option] = value
    debug_msg('updating config option |%s| to |%s|' % (option, value))
    return weechat.WEECHAT_RC_OK
