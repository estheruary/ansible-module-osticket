Ansible Module for osTicket
=========

Provides a module to create tickets in osTicket using its
[API](https://docs.osticket.com/en/latest/Developer%20Documentation/API%20Docs.html)

Requirements
------------

You will need an API key in order to use the osTicket API but the module itself
has no prereqs.

Role Variables
--------------

This module does not rely on any external variables.

Dependencies
------------

No additional dependencies outside what is required for Ansible itself.

Example Playbook
----------------

    - hosts: servers
      roles:
        - ansible-module-osticket
      tasks:
        - name: Create a new ticket.
	  osticket:
	  ...

License
-------

GPLv3+

Author Information
------------------

* Estelle Poulin [dev@inspiredby.es](mailto:dev@inspiredby.es).
