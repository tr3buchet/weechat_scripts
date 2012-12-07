"""
Author: Trey Morris <treyemorris@gmail.com>
Homepage: https://github.com/tr3buchet/weechat_sendmail_notify.py/
Version: 1.0

This plugin is for using sendmail to send notifications
"""

import weechat
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

# register script
weechat.register('sendmail_notify', 'Trey Morris', '1.0',
                 'Some License',
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
    """Callback called when highlight or private message is received"""
    msg = MIMEText(signal_data)
    msg['From'] = config['from']
    msg['To'] = config['to']
    msg['Subject'] = signal
    p = Popen(['/usr/sbin/sendmail', '-t'], stdin=PIPE)
    p.communicate(msg.as_string())

    return weechat.WEECHAT_RC_OK


def config_callback(data, option, value):
    """Callback called when a script option is changed."""
    weechat.prnt('', 'config callback |%s|%s|%s|' % (data, option, value))
    return weechat.WEECHAT_RC_OK
