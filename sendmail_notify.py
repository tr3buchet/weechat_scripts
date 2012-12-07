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
    if not config.get(option):
        weechat.prnt('', weechat.prefix('error') + 'sendmail_notify: '
                     'please set option |%s|' % option)


# setup hooks
weechat.hook_signal('weechat_highlight', 'send_message', '')
weechat.hook_signal('weechat_pv', 'send_message', '')
weechat.hook_config("plugins.var.python.sendmail_notify.*",
                    "config_callback", "")


def send_message(data, signal, signal_data):
    """Callback called when highlight or private message is received.
       Creates an email and uses subprocess to call sendmail to send it.
    """
    msg = MIMEText(signal_data)
    msg['From'] = config['from']
    msg['To'] = config['to']
    msg['Subject'] = signal
    weechat.prnt('', weechat.prefix('debug') + 'sendmail_notify: '
                 'sending |%s|%s|%s|%s|' % (config['from'], config['to'],
                                            signal, signal_data))
    p = Popen(['/usr/sbin/sendmail', '-t'], stdin=PIPE)
    p.communicate(msg.as_string())

    return weechat.WEECHAT_RC_OK


def config_callback(data, option, value):
    """Callback called when a script option is changed.
       Stores the config value so it can be retrieved locally when sending
       messages. (may be an unnecessary optimization)
    """
    option = option.split('.')[-1]
    config[option] = value
    return weechat.WEECHAT_RC_OK
