#!/usr/bin/env python

"""Tests for `gpm_precipitation_tools` package."""


import unittest
from click.testing import CliRunner

from gpm_precipitation_tools import gpm_precipitation_tools
from gpm_precipitation_tools import cli


class TestGpm_precipitation_tools(unittest.TestCase):
    """Tests for `gpm_precipitation_tools` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'gpm_precipitation_tools.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
