# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the niceman package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Functions to read and manipulate reprozip yaml files

"""
from __future__ import unicode_literals

import collections

import datetime
import niceman
import niceman.interface.retrace
import niceman.utils as utils
import yaml
import io


def load_config(filename):
    """Parses a ReproZip YAML file into a configuration object

    Given the path to a ReproZip YAML file, it parses the file and
    stores the resulting environment configuration into an object.

    Parameters
    ----------
    filename : str
        Path to the ReproZip YAML file

    Return
    ------
    dict
        The environment configuration

    """
    with io.open(filename, encoding='utf-8') as fp:
        config = yaml.safe_load(fp)
        # TODO: Check version of ReproZip file and warn if unknown
        return config


def write_config(output, config):
    """Writes an environment config to a stream

    Parameters
    ----------
    output
        Output Stream

    config : dict
        Environment configuration (input)

    """

    # Allow yaml to handle OrderedDict
    # From http://stackoverflow.com/questions/31605131
    if collections.OrderedDict not in yaml.SafeDumper.yaml_representers:
        yaml.SafeDumper.add_representer(
            collections.OrderedDict,
            lambda self, data:
            self.represent_mapping('tag:yaml.org,2002:map', data.items()))

    envconfig = dict(config)  # Shallow copy for destruction
    output.write(("# NICEMAN Environment Configuration File\n" +
                  "# This file was created by NICEMAN {0} on {1}\n").format(
        niceman.__version__, datetime.datetime.now()))

    c = "\n# Runs: Commands and related environment variables\n\n"
    write_config_key(output, envconfig, "runs", c)

    c = "\n# Package Origins \n\n"
    write_config_key(output, envconfig, "origins", c)

    c = "\n# Packages \n\n"
    write_config_key(output, envconfig, "packages", c)

    c = "\n# Non-Packaged Files \n\n"
    write_config_key(output, envconfig, "other_files", c)

    if (envconfig):
        output.write("\n# Other ReproZip keys (not used by NICEMAN) \n\n")
        utils.safe_write(output, yaml.safe_dump(envconfig,
                                                encoding="utf-8",
                                                allow_unicode=True))


def write_config_key(os, envconfig, key, intro_comment=""):
    """Writes the YAML representation of a single key

    This writes a single key of a dict to an output stream and then removes
    the key from the dict.

    Parameters
    ----------
    os
        Output Stream
    envconfig
        Dictionary
    key
        Key from the dictionary
    intro_comment
        Optional introduction comment for the key

    """
    if key in envconfig:
        mini_config = dict()
        mini_config[key] = envconfig[key]
        del envconfig[key]
        utils.safe_write(os, intro_comment)
        utils.safe_write(os, yaml.safe_dump(mini_config,
                                            encoding="utf-8",
                                            allow_unicode=True))


def get_files(config, other_files=True):
    """Pulls the system files from a ReproZip configuration into a set

    Given a ReproZip configuration (read into a dictionary) it pulls
    the list of files from "packages" and "other files" sections into a
    set. It excludes files from "input_output".

    Parameters
    ----------
    config : dict
        ReproZip configuration
    other_files : bool, optional
        Either to return also other_files

    Return
    ------
    set
        Files listed in the configuration
    """

    files = set()

    if 'packages' in config:
        for package in config['packages']:
            if 'files' in package:
                files.update(package['files'])

    if other_files and 'other_files' in config:
        files.update(config["other_files"])

    return files
