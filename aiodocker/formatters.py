from collections import defaultdict, namedtuple
from datetime import datetime
import dateutil.parser
import shlex
from aiodocker.exceptions import CompareError, SparseError

Port = namedtuple('Port', 'port protocol bindings')
Field = namedtuple('Field', 'name aliases func')
SearchResult = namedtuple('SearchResult', ['name',
                                           'is_official',
                                           'is_trusted',
                                           'star_count',
                                           'description'])


class Container(dict):

    def compare(self, other):
        """
        Allows to compare by id, names and name.

        Parameters:
            other (dict): a comparable dict
        Raises:
            CompareError
            SparseError
        """
        if not isinstance(other, dict):
            raise CompareError('other has the wrong type')

        fields = ('id', 'name', 'names')
        comparable = any(field in other for field in fields)
        if not comparable:
            raise CompareError('any of {} is required'.format(fields))

        if 'id' in other:
            if 'id' not in self:
                raise SparseError('self is too sparse')
            largest, smallest = other['id'], self['id']
            if len(other['id']) < len(self['id']):
                largest, smallest = self['id'], other['id']
            if not largest.startswith(smallest):
                return False

        if 'name' in other:
            names = self.get('names', [])
            if 'name' in self:
                names.append(self['name'])
            if not names:
                raise SparseError('self is too sparse')
            if other['name'] not in self['names']:
                return False
        return True

    __eq__ = compare


class Image(dict):

    def compare(self, other):
        """
        Allows to compare by repo_tags or id.

        Parameters:
            other (dict): a comparable dict
        Raises:
            CompareError
            SparseError
        """
        if not isinstance(other, dict):
            raise CompareError('other has the wrong type')

        fields = ('repo_tag', 'id')
        comparable = any(field in other for field in fields)
        if not comparable:
            raise CompareError('any of {} is required'.format(fields))

        if 'id' in other:
            if 'id' not in self:
                raise SparseError('self is too sparse')
            largest, smallest = other['id'], self['id']
            if len(other['id']) < len(self['id']):
                largest, smallest = self['id'], other['id']
            if not largest.startswith(smallest):
                return False

        if 'repo_tag' in other:
            tags = self.get('repo_tags', [])
            if 'repo_tag' in self:
                tags.append(self['repo_tag'])
            if not tags:
                raise SparseError('self is too sparse')
            if other['repo_tag'] not in tags:
                return False

        return True

    __eq__ = compare


def yield_fields(fields):
    return YieldFields(fields)


class YieldFields:
    def __init__(self, fields):
        self.fields = fields

    def __iter__(self):
        func = lambda x: x
        for field in self.fields:
            yield field.name, field.name, field.func or func
            for alias in field.aliases:
                yield field.name, alias, field.func or func

    def consume(self, data):
        response = {}
        for name, alias, func in self:
            if alias in data:
                response[name] = func(data.pop(alias))
        return response, data


def from_binds(data):
    response = data
    return response


def from_containers(data):
    return [from_container(elements) for elements in data]


def from_container(data):
    response, remains = vars(from_container)['fields'].consume(data)
    return Container(response)


def from_container_config(data):
    response, remains = vars(from_container_config)['fields'].consume(data)
    return response


def from_container_inspect(data):
    response, remains = vars(from_container_inspect)['fields'].consume(data)
    return response


def from_container_state(data):
    response, remains = vars(from_container_state)['fields'].consume(data)
    return response


def from_container_top(data):
    args = []
    for title in data['Titles']:
        title = title.lower()
        if title.startswith('%'):
            title = '%s_pers' % title[1:]
        args.append(title)
    Process = namedtuple('Process', args)
    len_split = len(args) - 1
    response = []
    for elt in data['Processes']:
        d = (' '.join(elt)).split(' ', len_split)
        response.append(Process(*d))
    return response


def from_devices(data):
    if data:
        return [from_device(element) for element in data]
    return []


def from_device(data):
    response, remains = vars(from_device)['fields'].consume(data)
    return response


def from_env(data):
    response = []
    for elt in data:
        a, b = elt.split('=', 1)
        response.append((a, b))
    return response


def from_exec_inspect(data):
    response, remains = vars(from_exec_inspect)['fields'].consume(data)
    return response


def from_exposed_ports(data):
    """
    >>> from_exposed_ports({'42/udp': [{}]})
    [Port(42, 'udp', {})]
    """
    response = []
    if data:
        for elt in data.keys():
            a, b = elt.split('/', 1)
            response.append(Port(a, int(b), {}))
    return response


def from_extra_hosts(data):
    """
    >>> from_extra_hosts(['foo:127.0.0.1'])
    [('foo', '127.0.0.1')]
    """
    response = []
    if data:
        for elt in data:
            a, b = elt.split(':', 1)
            response.append((a, b))
    return response


def from_history(data):
    return [from_history_log(elt) for elt in data]


def from_history_log(data):
    response, remains = vars(from_history_log)['fields'].consume(data)
    return response


def from_host_config(data):
    response, remains = vars(from_host_config)['fields'].consume(data)
    return response


def from_images(data):
    return [from_image(elt) for elt in data]


def from_image(data):
    response, remains = vars(from_image)['fields'].consume(data)
    return Image(response)


def from_image_inspect(data):
    response, remains = vars(from_image_inspect)['fields'].consume(data)
    return response


def from_info(data):
    response, remains = vars(from_info)['fields'].consume(data)
    return response


def from_isotime(data):
    """
    Convert iso 8601 time to python datetime.

    >>> from_isotime('2015-01-06T15:47:31.485331387Z')
    datetime(2015, 1, 6, 15, 47, 31, 485331, tzinfo=tzutc())
    """
    return dateutil.parser.parse(data)


def from_links(data):
    """
    >>> from_links(['foo:bar'])
    [('foo', 'bar')]
    """
    response = []
    if data:
        for elt in data:
            a, b = elt.split(':', 1)
            response.append((a, b))
    return response


def from_lxc_conf(data):
    return data


def from_network_mode(data):
    return data


def from_network_settings(data):
    response, remains = vars(from_network_settings)['fields'].consume(data)
    return response


def from_ports(data):
    return [from_port(elements) for elements in data]


def from_port(data):
    fields = yield_fields([
        Field('private_port', ('PrivatePort',), None),
        Field('public_port', ('PublicPort',), None),
        Field('protocol', ('Type',), None)
    ])

    response, remains = fields.consume(data)
    return response


def from_port_bindings(data):
    """
    >>> from_port_bindings({'42/udp': [{'HostPort': '22'}]})
    [Port(42, 'udp', {'host':22})]
    """
    response = []
    if data:
        for a, elt in data.items():
            b, c = a.split('/', 1)
            for d in elt:
                response.append(Port(int(b), c, {'host': int(d['HostPort'])}))
    return response


def from_restart_policy(data):
    response, remains = vars(from_restart_policy)['fields'].consume(data)
    return response


def from_search_results(data):

    def formatter(data):
        return SearchResult(**data)
    return [formatter(elements) for elements in data]


def from_unixtime(data):
    """
    >>> from_unixtime(1365714795)
    datetime(2013, 4, 11, 23, 13, 15, tzinfo=tzutc())
    """
    obj = datetime.fromtimestamp(data).strftime('%Y-%m-%dT%H:%M:%SZ')
    return dateutil.parser.parse(obj)


def from_version(data):
    response, remains = vars(from_version)['fields'].consume(data)
    return response


def from_volumes(data):
    """
    >>> from_volumes({'/tmp': {}})
    ['/tmp']
    """
    if data:
        return list(data.keys())
    return []


def from_volumes_from(data):
    response = []
    if data:
        for elt in data:
            if ':' in elt:
                a, b = elt.split(':', 1)
                response.append((a, b))
            else:
                response.append((a, None))
    return response


def to_binds(data):
    response = []
    for element in data:
        if isinstance(element, dict):
            value = '%s:%s' % (element['host_path'], element['container_path'])
            if element.get('ro'):
                value += ':ro'
            response.append(value)
        elif isinstance(element, (list, tuple)):
            value = '%s:%s' % (element[0], element[1])
            if len(element) > 2 and element[2] == 'ro':
                value += ':ro'
            response.append(value)
        else:
            response.append(element)
    return response


def to_container_config(data):
    response, remains = vars(to_container_config)['fields'].consume(data)
    return response


def to_devices(data):
    return [to_device(element) for element in data]


def to_device(data):
    response, remains = vars(to_device)['fields'].consume(data)
    return response


def to_env(data):
    """
    Converts to env

    >>> to_env('foo=bar baz=quz')
    'foo=bar baz=quz'

    >>> to_env(['foo=bar', 'baz=quz'])
    'foo=bar baz=quz'

    >>> to_env({'foo': 'bar', 'baz': 'quz'})
    'foo=bar baz=quz'
    """

    if isinstance(data, dict):
        parts = ['%s=%s' % (k, shlex.quote(v)) for k, v in data.items()]
        return ' '.join(parts)
    if isinstance(data, (list, set)):
        return ' '.join(parts)
    return data


def to_exposed_ports(data):
    """
    >>> to_exposed_ports([(42, 'udp', {}), (80, 'tcp')])
    {'42/udp': [{}], '80/tcp': [{}]}
    """
    response = {}
    for elt in data:
        a, b = elt[0], elt[1]
        response['%s/%s' % (a, b)] = {}
    return response


def to_extra_hosts(data):
    """
    >>> to_extra_hosts([('foo', '127.0.0.1')])
    ['foo:127.0.0.1']
    """
    response = []
    if isinstance(data, dict):
        data = data.items()
    for element in data:
        if isinstance(element, dict):
            response.append('%s:%s' % (element['hostname'], element['ip']))
        elif isinstance(element, (list, tuple)):
            response.append('%s:%s' % (element[0], element[1]))
        else:
            response.append(element)
    return response


def to_host_config(data):
    response, remains = vars(to_host_config)['fields'].consume(data)
    return response


def to_links(data):
    """
    >>> to_links([('foo', 'bar')])
    ['foo:bar']
    """
    response = []
    for elt in data:
        if isinstance(elt, dict):
            response.append('%s:%s' % (elt['container_name'], elt['alias']))
        elif isinstance(elt, (list, tuple)):
            response.append('%s:%s' % (elt[0], elt[1]))
        else:
            response.append(elt)
    return response


def to_lxc_conf(data):
    return data


def to_network_mode(data):
    return data


def to_port_bindings(data):
    """
    >>> to_port_bindings([(42, 'udp', 22)])
    {'42/udp': [{'HostPort': '22'}]}
    """
    response = defaultdict(dict)
    for element in data:
        if isinstance(element, dict):
            response['%s/%s' % (element['port'], element['protocol'])].append(
                {'HostPort': str(element['host_port'])}
            )
        elif isinstance(element, (list, tuple)):
            response['%s/%s' % (element[0], element[1])].append(
                {'HostPort': str(element[2])}
            )
    return dict(response)


def to_restart_policy(data):
    response, remains = vars(to_restart_policy)['fields'].consume(data)
    return response


def to_volumes_from(data):
    response = []
    for elt in data:
        a, b = None, None
        if isinstance(elt, (list, tuple)):
            if len(elt) == 2:
                a, b = elt
            else:
                a = elt[0]
        if b:
            response.append('%s:%s' % (a, b))
        else:
            response.append(a)
    return response


from_container.fields = yield_fields([
    Field('id', ('Id',), None),
    Field('image', ('Image',), None),
    Field('command', ('Command', 'Cmd'), None),
    Field('created', ('Created',), from_unixtime),
    Field('names', ('Names',), None),
    Field('status', ('Status',), None),
    Field('ports', ('Ports',), from_ports),
    Field('size_rw', ('SizeRw',), None),
    Field('size_root_fs', ('SizeRootFs',), None)
])

from_container_config.fields = yield_fields([
    Field('attach_stderr', ('AttachStderr',), None),
    Field('attach_stdin', ('AttachStdin',), None),
    Field('attach_stdout', ('AttachStdout',), None),
    Field('cmd', ('Cmd', 'Command'), None),
    Field('cpu_shares', ('CpuShares',), None),
    Field('cpuset', ('Cpuset',), None),
    Field('domainname', ('Domainname',), None),
    Field('entrypoint', ('Entrypoint',), None),
    Field('env', ('Env',), from_env),
    Field('exposed_ports', ('ExposedPorts',), from_exposed_ports),
    Field('hostname', ('Hostname',), None),
    Field('image', ('Image',), None),
    Field('mac_address', ('MacAddress',), None),
    Field('memory', ('Memory',), None),
    Field('memory_swap', ('MemorySwap',), None),
    Field('network_disabled', ('NetworkDisabled',), None),
    Field('on_build', ('OnBuild',), None),  # special
    Field('open_stdin', ('OpenStdin',), None),
    Field('port_specs', ('PortSpecs',), None),  # special
    Field('stdin_once', ('StdinOnce',), None),
    Field('tty', ('Tty',), None),
    Field('user', ('User',), None),

    # from image inspect

    Field('volumes', ('Volumes',), from_volumes),
    Field('volumes_from', ('VolumesFrom',), from_volumes_from),
    Field('working_dir', ('WorkingDir',), None),
])

from_container_inspect.fields = yield_fields([
    Field('app_armor_profile', ('AppArmorProfile',), None),
    Field('applied_volumes_from', ('AppliedVolumesFrom',), None),  # exec inspects
    Field('args', ('Args',), None),
    Field('config', ('Config',), from_container_config),
    Field('created', ('Created',), from_isotime),
    Field('driver', ('Driver',), None),
    Field('exec_driver', ('ExecDriver',), None),
    Field('exec_ids', ('ExecIDs',), None),
    Field('host_config', ('HostConfig',), from_host_config),
    Field('hostname_path', ('HostnamePath',), None),
    Field('hosts_path', ('HostsPath',), None),
    Field('id', ('Id',), None),
    Field('image', ('Image',), None),
    Field('mount_label', ('MountLabel',), None),
    Field('name', ('Name',), None),
    Field('network_settings', ('NetworkSettings',), from_network_settings),
    Field('path', ('Path',), None),
    Field('process_label', ('ProcessLabel',), None),
    Field('resolv_conf_path', ('ResolvConfPath',), None),
    Field('restart_count', ('RestartCount',), None),
    Field('state', ('State',), from_container_state),
    Field('update_dns', ('UpdateDns',), None),  # exec inspects
    Field('volumes', ('Volumes',), from_volumes),
    Field('volumes_rw', ('VolumesRW',), None)
])

from_container_state.fields = yield_fields([
    Field('error', ('Error',), None),
    Field('exit_code', ('ExitCode',), None),
    Field('finished_at', ('FinishedAt',), from_isotime),
    Field('oom_killed', ('OOMKilled',), None),
    Field('paused', ('Paused',), None),
    Field('pid', ('Pid',), None),
    Field('restarting', ('Restarting',), None),
    Field('running', ('Running',), None),
    Field('started_at', ('StartedAt',), from_isotime),
])

from_device.fields = yield_fields([
    Field('path_on_host', ('PathOnHost',), None),
    Field('path_in_container', ('PathInContainer',), None),
    Field('cgroup_permissions', ('CgroupPermissions'), None),
])

from_exec_inspect.fields = yield_fields([
    Field('container', ('Container',), from_container_inspect),
    Field('exit_code', ('ExitCode',), None),
    Field('id', ('ID',), None),
    Field('open_stderr', ('OpenStderr',), None),
    Field('open_stdin', ('OpenStdin',), None),
    Field('open_stdout', ('OpenStdout',), None),
    Field('process_config', ('ProcessConfig',), None),
    Field('running', ('Running',), None),
])

from_history_log.fields = yield_fields([
    Field('id', ('Id',), None),
    Field('created', ('Created',), from_unixtime),
    Field('created_by', ('CreatedBy',), None),
])

from_host_config.fields = yield_fields([
    Field('binds', ('Binds',), from_binds),
    Field('cap_add', ('CapAdd',), None),
    Field('cap_drop', ('CapDrop',), None),
    Field('container_id_file', ('ContainerIDFile',), None),
    Field('devices', ('Devices',), from_devices),
    Field('dns', ('Dns',), None),
    Field('dns_search', ('DnsSearch',), None),
    Field('extra_hosts', ('ExtraHosts',), from_extra_hosts),
    Field('ipc_mode', ('IpcMode',), None),
    Field('links', ('Links',), from_links),
    Field('lxc_conf', ('LxcConf',), from_lxc_conf),
    Field('network_mode', ('NetworkMode',), from_network_mode),
    Field('port_bindings', ('PortBindings',), from_port_bindings),
    Field('privileged', ('Privileged',), None),
    Field('readonly_rootfs', ('ReadonlyRootfs',), None),
    Field('publish_all_ports', ('PublishAllPorts',), None),
    Field('restart_policy', ('RestartPolicy',), from_restart_policy),
    Field('security_opt', ('SecurityOpt',), None),
    Field('volumes_from', ('VolumesFrom',), from_volumes_from)
])

from_image.fields = yield_fields([
    Field('repo_tags', ('RepoTags',), None),
    Field('id', ('Id',), None),
    Field('created', ('Created',), from_unixtime),
    Field('size', ('Size',), None),
    Field('virtual_size', ('VirtualSize',), None),
])

from_image_inspect.fields = yield_fields([
    Field('Created', ('Created',), from_isotime),
    Field('Container', ('Container',), None),
    Field('ContainerConfig', ('ContainerConfig',), from_container_config),
    Field('Id', ('Id',), None),
    Field('Parent', ('Parent',), None),
    Field('Size', ('Size',), None),
])

from_info.fields = yield_fields([
    Field('containers', ('Containers',), None),
    Field('images', ('Images',), None),
    Field('driver', ('Driver',), None),
    Field('driver_status', ('DriverStatus',), None),
    Field('execution_driver', ('ExecutionDriver',), None),
    Field('kernel_version', ('KernelVersion',), None),
    Field('ncpu', ('NCPU',), None),
    Field('memory_total', ('MemTotal',), None),
    Field('name', ('Name',), None),
    Field('id', ('ID',), None),
    Field('debug', ('Debug',), None),
    Field('NFd', ('NFd',), None),
    Field('NGoroutines', ('NGoroutines',), None),
    Field('NEventsListener', ('NEventsListener',), None),
    Field('init_path', ('InitPath',), None),
    Field('init_sha1', ('InitSha1',), None),
    Field('index_server_address', ('IndexServerAddress',), None),
    Field('memory_limit', ('MemoryLimit',), None),
    Field('swap_limit', ('SwapLimit',), None),
    Field('ipv4_forwarding', ('IPv4Forwarding',), None),
    Field('labels', ('Labels',), None),
    Field('docker_root_dir', ('DockerRootDir',), None),
    Field('operating_system', ('OperatingSystem',), None),
])

from_network_settings.fields = yield_fields([
    Field('bridge', ('Bridge',), None),
    Field('gateway', ('Gateway',), None),
    Field('global_ipv6_address', ('GlobalIPv6Address',), None),  # exec inspect
    Field('global_ipv6_address_len', ('GlobalIPv6PrefixLen',), None),  # exec inspect
    Field('gateway', ('Gateway',), None),
    Field('ipv6_gateway', ('IPv6Gateway',), None),  # exec inspect
    Field('ip_address', ('IPAddress',), None),
    Field('ip_prefix_len', ('IPPrefixLen',), None),
    Field('link_local_ipv6_address', ('LinkLocalIPv6Address',), None),  # exec inspect
    Field('link_local_ipv6_prefix_len', ('LinkLocalIPv6PrefixLen',), None),  # exec inspect
    Field('mac_address', ('MacAddress',), None),
    Field('port_mapping', ('PortMapping',), None),
    Field('ports', ('Ports',), None)
])

from_restart_policy.fields = yield_fields([
    Field('maximum_retry_count', ('MaximumRetryCount',), None),
    Field('name', ('Name',), None),
])

from_version.fields = yield_fields([
    Field('api_version', ('ApiVersion',), None),
    Field('arch', ('Arch',), None),
    Field('git_commit', ('GitCommit', 'Cmd'), None),
    Field('go_version', ('GoVersion',), None),
])

to_container_config.fields = yield_fields([
    Field('AttachStdin', ('attach_stdin',), None),
    Field('AttachStdout', ('attach_stdout',), None),
    Field('AttachStderr', ('attach_stderr',), None),
    Field('Cmd', ('cmd', 'command'), None),
    Field('CpuShares', ('cpu_shares',), None),
    Field('Cpuset', ('cpuset',), None),
    Field('Domainname', ('domainname',), None),
    Field('Entrypoint', ('entrypoint',), None),
    Field('Env', ('env',), to_env),
    Field('ExposedPorts', ('exposed_ports',), to_exposed_ports),
    Field('HostConfig', ('host_config',), to_host_config),  # special
    Field('Hostname', ('hostname',), None),
    Field('Image', ('image',), None),
    Field('MacAddress', ('mac_address',), None),
    Field('Memory', ('memory',), None),
    Field('MemorySwap', ('memory_swap',), None),
    Field('NetworkDisabled', ('network_disabled',), None),
    Field('OpenStdin', ('open_stdin',), None),
    Field('SecurityOpts', ('security_opts',), None),  # special
    Field('StdinOnce', ('stdin_once',), None),
    Field('Tty', ('tty',), None),
    Field('Volumes', ('volumes',), None),  # special
    Field('WorkingDir', ('working_dir',), None),  # special
    Field('User', ('user',), None),
])

to_device.fields = yield_fields([
    Field('PathOnHost', ('path_on_host',), None),
    Field('PathInContainer', ('path_in_container',), None),
    Field('CgroupPermissions', ('cgroup_permissions'), None),
])

to_host_config.fields = yield_fields([
    Field('Binds', ('binds',), to_binds),
    Field('Links', ('links',), to_links),
    Field('LxcConf', ('lxc_conf',), to_lxc_conf),
    Field('PortBindings', ('port_bindings',), to_port_bindings),
    Field('PublishAllPorts', ('publish_all_ports',), None),
    Field('Privileged', ('privileged',), None),
    Field('ReadonlyRootfs', ('readonly_rootfs',), None),
    Field('Dns', ('dns',), None),
    Field('DnsSearch', ('dns_search',), None),
    Field('ExtraHosts', ('extra_hosts',), to_extra_hosts),
    Field('VolumesFrom', ('volumes_from',), to_volumes_from),
    Field('CapAdd', ('cap_add',), None),
    Field('CapDrop', ('cap_drop',), None),
    Field('RestartPolicy', ('restart_policy',), to_restart_policy),
    Field('NetworkMode', ('network_mode',), to_network_mode),
    Field('Devices', ('devices',), to_devices)
])

to_restart_policy.fields = yield_fields([
    Field('MaximumRetryCount', ('maximum_retry_count',), None),
    Field('Name', ('name',), None),
])
