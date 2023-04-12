#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
from hvac.exceptions import InvalidPath

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_auth_ldap
version_added: "3.17.7"
short_description: Hashicorp Vault ldap configuration module
description:
    - Module to configure the LDAP authentication method in Hashicorp Vault.
options:
    mount_point:
        description:
            - location where this auth_method is mounted. also known as "path"
    ldap_url:
        description:
            - The LDAP server to connect to. Examples: ldap://ldap.myorg.com
        default: ldap://127.0.0.1
    anonymous_group_search:
        description:
            - Use anonymous binds when performing LDAP group searches (note: even when true,
              the initial credentials will still be used for the initial connection test).
        default: False
    request_timeout:
        description:
            - Timeout, in seconds, for the connection when making requests against the server before
              returning back an error.
        default: 90
    token_bound_cidrs:
        description:
            - List of CIDR blocks; if set, specifies blocks of IP addresses which can authenticate
              successfully, and ties the resulting token to these blocks as well.
        default: []
    token_explicit_max_ttl:
        description:
            - If set, will encode an explicit max TTL onto the token. This is a hard cap even
              if token_ttl and token_max_ttl would otherwise allow a renewal.
        default: 0
    token_no_default_policy:
        description:
            - If set, the default policy will not be set on generated tokens; otherwise it
              will be added to the policies set in token_policies.
        default: False
    token_num_uses:
        description:
            - The maximum number of times a generated token may be used (within its lifetime); 0 means
              unlimited.
        default: 0
    token_period:
        description:
            - The maximum allowed period value when a periodic token is requested from this role.
        default: 0
    token_policies:
        description:
            - List of token policies to encode onto generated tokens.
        default: []
    token_type:
        description:
            - The type of token that should be generated.
        default: default
    userfilter:
        description:
            - An optional LDAP user search filter.
        default: ({{.UserAttr}}={{.Username}})
    username_as_alias:
        description:
            - If set to true, forces the auth method to use the username passed by the user as the
            alias name.
        default: False
    case_sensitive_names:
        description:
            - If set, user and group names assigned to policies within the backend will be case sensitive. Otherwise,
              names will be normalized to lower case. Case will still be preserved when sending the username to the LDAP
              server at login time; this is only for matching local user/group definitions.
        default: False
    starttls:
        description:
            - If true, issues a StartTLS command after establishing an unencrypted connection
        default: False
    tls_min_version:
        description:
            - Minimum TLS version to use. Accepted values are tls10, tls11 or tls12
        default: tls12
    tls_max_version:
        description:
            - Maximum TLS version to use. Accepted values are tls10, tls11 or tls12
        default: tls12
    insecure_tls:
        description:
            -  If true, skips LDAP server SSL certificate verification
        default: False
    certificate:
        description:
            - CA certificate to use when verifying LDAP server certificate, must be x509 PEM encoded
        default: ''
    binddn:
        description:
         - Distinguished name of object to bind when performing user search.
           Example cn=vault,ou=Users,dc=example,dc=com
        default: ''
        aliases: ['bind_dn']
    bindpass:
        description:
            - Password to use along with binddn when performing user search
        default: None
        aliases: ['bind_pass']
    userdn:
        description:
            - Base DN under which to perform user search. Example: ou=Users,dc=example,dc=com
        default: ''
        aliases: ['user_dn']
    userattr:
        description:
         - Attribute on user attribute object matching the username passed when authenticating.
           Examples sAMAccountName, cn, uid
        default: cn
        aliases: ['user_attr']
    discoverdn:
        description:
         - Use anonymous bind to discover the bind DN of a user
        default: False
        aliases: ['discover_dn']
    deny_null_bind:
        description:
         - This option prevents users from bypassing authentication when providing an empty password
        default: True
    upndomain:
        description:
         - The userPrincipalDomain used to construct the UPN string for the authenticating user
        default: ''
        aliases: ['upn_domain']
    groupfilter:
        description:
            - Go template used when constructing the group membership query. The template can access the following
              context variables [UserDN, Username]
        default: (|(memberUid={{.Username}})(member={{.UserDN}})(uniqueMember={{.UserDN}}))
        aliases: ['group_filter']
    groupattr:
        description:
            - LDAP attribute to follow on objects returned by groupfilter in order to enumerate user group membership
        default: 'cn'
        aliases: ['group_attr']
    groupdn:
        description:
            - LDAP search base to use for group membership search
        default: ''
        aliases: ['group_dn']
    token_ttl:
        description:
            - The incremental lifetime for generated tokens
        default: ''
    token_max_ttl:
        description:
            - The maximum lifetime for generated tokens
        default: ''
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_auth_ldap:
        userdn: "{{ auth_ldap_userdn }}"
        groupdn: "{{ auth_ldap_groupdn }}"
        binddn: "{{ auth_ldap_binddn }}"
        ldap_url: "{{ auth_ldap_url }}"
        insecure_tls: "{{ auth_ldap_insecure_tls }}"
        groupfilter: "{{ auth_ldap_groupfilter }}"
        upndomain: "{{ auth_ldap_upndomain }}"
'''


def main():
    # separate long default value to pass linting
    default_groupfilter = '(|(memberUid={{.Username}})(member={{.UserDN}})(uniqueMember={{.UserDN}}))'
    default_userfilter = '({{.UserAttr}}={{.Username}})'
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='ldap')
    argspec['anonymous_group_search'] = dict(required=False, type='bool', default=False)
    argspec['binddn'] = dict(required=False, type='str', default='', aliases=['bind_dn'])
    argspec['bindpass'] = dict(required=False, type='str', default=None, no_log=True, aliases=['bind_pass'])
    argspec['case_sensitive_names'] = dict(required=False, type='bool', default=False)
    argspec['certificate'] = dict(required=False, type='str', default='')
    argspec['deny_null_bind'] = dict(required=False, type='bool', default=True)
    argspec['discoverdn'] = dict(required=False, type='bool', default=False, aliases=['discover_dn'])
    argspec['groupattr'] = dict(required=False, type='str', default='cn', aliases=['group_attr'])
    argspec['groupdn'] = dict(required=False, type='str', default='', aliases=['group_dn'])
    argspec['groupfilter'] = dict(required=False, type='str', default=default_groupfilter, aliases=['group_filter'])
    argspec['insecure_tls'] = dict(required=False, type='bool', default=False, aliases=[])
    argspec['request_timeout'] = dict(required=False, type='int', default=90)
    argspec['starttls'] = dict(required=False, type='bool', default=False)
    argspec['tls_max_version'] = dict(required=False, type='str', default='tls12')
    argspec['tls_min_version'] = dict(required=False, type='str', default='tls12')
    argspec['token_bound_cidrs'] = dict(required=False, type='list', default=[])
    argspec['token_explicit_max_ttl'] = dict(required=False, type='int', default=0)
    argspec['token_max_ttl'] = dict(required=False, type='int', default=0)
    argspec['token_no_default_policy'] = dict(required=False, type='bool', default=False)
    argspec['token_num_uses'] = dict(required=False, type='int', default=0)
    argspec['token_period'] = dict(required=False, type='int', default=0)
    argspec['token_policies'] = dict(required=False, type='list', default=[])
    argspec['token_ttl'] = dict(required=False, type='int', default=0)
    argspec['token_type'] = dict(required=False, type='str', default='default')
    argspec['upndomain'] = dict(required=False, type='str', default='', aliases=['upn_domain'])
    argspec['ldap_url'] = dict(required=False, type='str', default='ldap://127.0.0.1')
    argspec['use_token_groups'] = dict(required=False, type='bool', default=False)
    argspec['userattr'] = dict(required=False, type='str', default='cn', aliases=['user_attr'])
    argspec['userdn'] = dict(required=False, type='str', default='', aliases=['user_dn'])
    argspec['userfilter'] = dict(required=False, type='str', default=default_userfilter)
    argspec['username_as_alias'] = dict(required=False, type='bool', default=False)

    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_auth_ldap(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_auth_ldap(module):
    params = module.params
    client = hashivault_auth_client(params)
    changed = False
    mount_point = params.get('mount_point')
    desired_state = {
        'anonymous_group_search': params.get('anonymous_group_search'),
        'binddn': params.get('binddn'),
        'bindpass': params.get('bindpass'),
        'case_sensitive_names': params.get('case_sensitive_names'),
        'certificate': params.get('certificate'),
        'deny_null_bind': params.get('deny_null_bind'),
        'discoverdn': params.get('discoverdn'),
        'groupattr': params.get('groupattr').lower(),
        'groupdn': params.get('groupdn'),
        'groupfilter': params.get('groupfilter'),
        'insecure_tls': params.get('insecure_tls'),
        'request_timeout': params.get('request_timeout'),
        'starttls': params.get('starttls'),
        'tls_max_version': params.get('tls_max_version'),
        'tls_min_version': params.get('tls_min_version'),
        'token_bound_cidrs': params.get('token_bound_cidrs'),
        'token_explicit_max_ttl': params.get('token_explicit_max_ttl'),
        'token_max_ttl': params.get('token_max_ttl'),
        'token_no_default_policy': params.get('token_no_default_policy'),
        'token_num_uses': params.get('token_num_uses'),
        'token_period': params.get('token_period'),
        'token_policies': params.get('token_policies'),
        'token_ttl': params.get('token_ttl'),
        'token_type': params.get('token_type'),
        'upndomain': params.get('upndomain'),
        'url': params.get('ldap_url'),
        'use_pre111_group_cn_behavior': params.get('use_pre111_group_cn_behavior'),
        'use_token_groups': params.get('use_token_groups'),
        'userattr': params.get('userattr').lower(),
        'userdn': params.get('userdn'),
        'userfilter': params.get('userfilter'),
        'username_as_alias': params.get('username_as_alias')
    }

    # if bind pass is None, remove it from desired state since we can't compare
    if desired_state['bindpass'] is None:
        del desired_state['bindpass']

    # check current config
    current_state = dict()
    try:
        result = client.auth.ldap.read_configuration(
            mount_point=mount_point)['data']
        current_state = result
    except InvalidPath:
        pass

    # check if current config matches desired config values, if they match, set changed to false to prevent action
    for k, v in desired_state.items():
        if k != "bindpass":
            try:
                if v != current_state[k]:
                    changed = True
            except KeyError as e:
                return {'failed': True, 'msg': "HVAC unsupported parameter: " + str(e)}
            except Exception as e:
                return {'failed': True, 'msg': str(e)}

    # if configs dont match and checkmode is off, complete the change
    if changed and not module.check_mode:
        client.auth.ldap.configure(**desired_state)

    return {
        'changed': changed,
        "diff": {
            "before": current_state,
            "after": desired_state,
        }
    }


if __name__ == '__main__':
    main()
