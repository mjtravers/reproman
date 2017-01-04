# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the repronim package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

import logging
from mock import patch, call, MagicMock

from ...utils import swallow_logs
from ...tests.utils import assert_in
from ..ec2environment import Ec2Environment

def test_ec2environment_class():

    config = {
        'resource_type': 'ec2-environment',
        'resource_client': 'my-aws-subscription',
        'region_name': 'us - east - 1',
        'instance_type': 't2.micro',
        'security_group': 'SSH only',
        'key_name': 'aws-key-name',
        'key_filename': '/path/to/id_rsa',
        'config_path': '/path/to/config/file',
    }

    with patch('boto3.resource') as MockEc2Client, \
        patch('repronim.resource.Resource.factory') as MockResourceClient, \
        patch('repronim.support.sshconnector2.SSHConnector2.__enter__') as MockSSH, \
            swallow_logs(new_level=logging.DEBUG) as log:

        # Test initializing the environment object.
        env = Ec2Environment(config)
        calls = [
            call('my-aws-subscription', config_path='/path/to/config/file'),
            call().get_config('aws_access_key_id'),
            call().get_config('aws_secret_access_key'),
        ]
        MockResourceClient.assert_has_calls(calls, any_order=True)

        # Test creating an environment.
        name = 'my-test-environment'
        image_id = 'ubuntu:trusty'
        env.create(name, image_id)
        assert env.get_config('name') == 'my-test-environment'
        assert env.get_config('base_image_id') == 'ubuntu:trusty'

        # Test running some install commands.
        command = ['apt-get', 'install', 'bc']
        env.add_command(command)
        command = ['apt-get', 'install', 'xeyes']
        env.add_command(command)
        env.execute_command_buffer()
        calls = [
            call()('apt-get install bc'),
            call()('apt-get install xeyes'),
        ]
        MockSSH.assert_has_calls(calls, any_order=True)
        assert_in("Running command '['apt-get', 'install', 'bc']'", log.lines)
        assert_in("Running command '['apt-get', 'install', 'xeyes']'", log.lines)