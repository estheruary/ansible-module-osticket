#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Estelle Poulin <dev@inspiredby.es>
# Inspired by mattermost module.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

DOCUMENTATION = """
module: osticket
short_description: Create tickets in osTicket
description:
    - Creates tickets in your osTicket using the web API.
version_added: "2.8"
author: "Estelle Poulin <dev@inspiredby.es>"
options:
  url:
    description:
      - The URL of your osTicket server.
    required: true
  api_key:
    description:
      - osTicket API key. Log into your osTicket site, go to Admin Panel ->
        Manage -> API Keys.
  alert:
    description:
      - Send an alert to staff.
    required: false
    default: true
    type: bool
  autorespond:
    description:
      - Enable autoresponses for this ticket.
    required: false
    default: true
    type: bool
  ip:
    description:
      - The IP address of the submitter.
    required: false
  priority:
    description:
      - The priority ID associated with the ticket.
    required: false
    default: 'Normal'
  source:
    description:
      - The source of the ticket.
    required: false
    default: 'API'
  topicid:
    description:
      - The help topic id associated with the ticket.
    required: false
  attachments:
    description:
      - A list of attachments to add to the ticket. See examples.
  custom_fields:
    description:
      - Key-value pairs corrisponding to your ticket creation form. See
        examples.
    required: false
  validate_certs:
    description:
      - Validate certificates on TLS endpoints.
    required: false
    defaults: true
    type: bool
"""

EXAMPLES = """
- name: Create a ticket.
  osticket:
    url: https://osticket.example.com
    api_key: my_api_key
    name: 'Jane Doe'
    email: jane.doe@example.com'
    subject: 'Printer might be out of ink.'
    message: 'Screen flashes an error about a squid."'

- name: Create a ticket with attachments.
    url: https://osticket.example.com
    api_key: my_api_key
    name: 'John Smith'
    email: john.smith@example.com'
    subject: 'Monitor has black spot.'
    message: 'I think it might be broken. See attached screenshot.'
    attachments:
      -
        name: 'Screenshot.png'
        type: 'image/png'
        data: '{{ lookup("file", "Screenshot.png") | b64encode }}'
        encoding: base64

- name: Create a ticket with additional information.
    url: https://osticket.example.com
    api_key: my_api_key
    name: 'Jean Dupont'
    email: jean.dupont@example.com'
    subject: 'S'il te plait appelle moi.'
    message: 'Je suis seul.'
    custom_fields:
      phone: '05 70 27 14 91'
"""


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            url=dict(type='str', required=True),
            api_key=dict(type='str', required=True, no_log=True),
            name=dict(type='str', required=True),
            email=dict(type='str', required=True),
            subject=dict(type='str', required=True),
            message=dict(type='str', required=True),
            message_mime=dict(type='str', default='text/plain'),
            alert=dict(type='bool', default=True),
            autorespond=dict(type='bool', default=True),
            ip=dict(type='str', required=False),
            priority=dict(type='str', required=False),
            source=dict(type='str', requied=False),
            topicid=dict(type='str', required=False),
            attachments=dict(type='list', required=False),
            custom_fields=dict(type='dict', required=False),
            validate_certs=dict(default=True, type='bool'),
        )
    )
    
    result = {
        'changed': False,
        'msg': 'OK',
    }

    api_url = "{}/api/tickets.json".format(module.params['url'])
    print(api_url)
    
    data = {
        'name': module.params['name'],
        'email': module.params['email'],
        'subject': module.params['subject'],
    }

    message_mime = module.params['message_mime'] or 'text/plain'

    data['message'] = "data:{},{}".format(message_mime,
                                          module.params['message'])

    opt_args = [
        'alert',
        'autorespond',
        'ip',
        'priority',
        'source',
        'topicid'
    ]

    for opt in opt_args:
        if module.params[opt]:
            data[opt] = module.params[opt]

    # Attachments is a list of dicts.
    # attachments:
    # -
    #   name: 'Example'
    #   data: '{{ lookup('file', 'example.txt') | urlencode }}
    #   type: 'text/plain'
    #   encoding: 'base64'
    if module.params['attachments']:
        data['attachments'] = []
        for at in module.params['attachments']:
            if not at['name']:
                result['msg'] = 'Prameter name for attachment not found.'
                module.fail_json(**result)

            if not at['data']:
                result['msg'] = 'Parameter data for attachment not found.'
                module.fail_json(**result)

            data_uri = 'data:'

            if at['type']:
                data_uri += at['type']

            if at['encoding']:
                data_uri += ";{}".format(at['encoding'])

            data_uri += ',{}'.format(at['data'])

            data['attachments'].append({
                module.params['name']: data_uri
            })

    if module.params['custom_fields']:
        data.update(module.params['custom_fields'])

    data = module.jsonify(data)

    headers = {
        'Content-Type': 'application/json',
        'Accerpt': 'application/json',
        'X-API-Key': "{}".format(module.params['api_key'])
    }

    # osTicket's API doesn't expose any way to test a query.
    if not module.check_mode:
        _, info = fetch_url(
            module.module,
            url=api_url,
            headers=headers,
            method='POST',
            data=data)

        if info['status'] != 200:
            result['msg'] = "Submit ticket failed, the error was: {}".format(
                info['msg'])
            module.fail_json(**result)

        module.exit_json(**result)

if __name__ == '__main__':
    main()
