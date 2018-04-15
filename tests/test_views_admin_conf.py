""" venv/bin/python probemanager/manage.py test bro.tests.test_views_admin_conf --settings=probemanager.settings.dev """
from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from bro.models import Configuration


class ViewsConfAdminTest(TestCase):
    fixtures = ['init', 'crontab', 'test-core-secrets', 'test-bro-signature',
                'test-bro-script', 'test-bro-ruleset', 'test-bro-source', 'test-bro-conf',
                'test-bro-bro']

    def setUp(self):
        self.client = Client()
        User.objects.create_superuser(username='testuser', password='12345', email='testuser@test.com')
        if not self.client.login(username='testuser', password='12345'):
            self.assertRaises(Exception("Not logged"))
        self.date_now = timezone.now()

    def tearDown(self):
        self.client.logout()

    def test_conf(self):
        response = self.client.get('/admin/bro/configuration/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Configuration.get_all()), 1)
        response = self.client.post('/admin/bro/configuration/add/', {'name': 'conftest',
                                                                      "my_scripts": "/usr/local/bro/share/bro/site/myscripts.bro",
                                                                      "my_signatures": "/usr/local/bro/share/bro/site/mysignatures.sig",
                                                                      "policydir": "/usr/local/bro/share/bro/policy/",
                                                                      "bin_directory": "/usr/local/bro/bin/",
                                                                      "broctl_cfg": "/usr/local/bro/etc/broctl.cfg",
                                                                      "broctl_cfg_text": "## Global BroControl configuration file.\r\n\r\n###############################################\r\n# Mail Options\r\n\r\n# Recipient address for all emails sent out by Bro and BroControl.\r\nMailTo = root@localhost\r\n\r\n# Mail connection summary reports each log rotation interval.  A value of 1\r\n# means mail connection summaries, and a value of 0 means do not mail\r\n# connection summaries.  This option has no effect if the trace-summary\r\n# script is not available.\r\nMailConnectionSummary = 1\r\n\r\n# Lower threshold (in percentage of disk space) for space available on the\r\n# disk that holds SpoolDir. If less space is available, \"broctl cron\" starts\r\n# sending out warning emails.  A value of 0 disables this feature.\r\nMinDiskSpace = 5\r\n\r\n# Send mail when \"broctl cron\" notices the availability of a host in the\r\n# cluster to have changed.  A value of 1 means send mail when a host status\r\n# changes, and a value of 0 means do not send mail.\r\nMailHostUpDown = 1\r\n\r\n###############################################\r\n# Logging Options\r\n\r\n# Rotation interval in seconds for log files on manager (or standalone) node.\r\n# A value of 0 disables log rotation.\r\nLogRotationInterval = 3600\r\n\r\n# Expiration interval for archived log files in LogDir.  Files older than this\r\n# will be deleted by \"broctl cron\".  The interval is an integer followed by\r\n# one of these time units:  day, hr, min.  A value of 0 means that logs\r\n# never expire.\r\nLogExpireInterval = 0\r\n\r\n# Enable BroControl to write statistics to the stats.log file.  A value of 1\r\n# means write to stats.log, and a value of 0 means do not write to stats.log.\r\nStatsLogEnable = 1\r\n\r\n# Number of days that entries in the stats.log file are kept.  Entries older\r\n# than this many days will be removed by \"broctl cron\".  A value of 0 means\r\n# that entries never expire.\r\nStatsLogExpireInterval = 0\r\n\r\n###############################################\r\n# Other Options\r\n\r\n# Show all output of the broctl status command.  If set to 1, then all output\r\n# is shown.  If set to 0, then broctl status will not collect or show the peer\r\n# information (and the command will run faster).\r\nStatusCmdShowAll = 0\r\n\r\n# Number of days that crash directories are kept.  Crash directories older\r\n# than this many days will be removed by \"broctl cron\".  A value of 0 means\r\n# that crash directories never expire.\r\nCrashExpireInterval = 0\r\n\r\n# Site-specific policy script to load. Bro will look for this in\r\n# $PREFIX/share/bro/site. A default local.bro comes preinstalled\r\n# and can be customized as desired.\r\nSitePolicyScripts = local.bro\r\n\r\n# Location of the log directory where log files will be archived each rotation\r\n# interval.\r\nLogDir = /usr/local/bro/logs\r\n\r\n# Location of the spool directory where files and data that are currently being\r\n# written are stored.\r\nSpoolDir = /usr/local/bro/spool\r\n\r\n# Location of other configuration files that can be used to customize\r\n# BroControl operation (e.g. local networks, nodes).\r\nCfgDir = /usr/local/bro/etc",
                                                                      "node_cfg": "/usr/local/bro/etc/node.cfg",
                                                                      "node_cfg_text": "# Example BroControl node configuration.\r\n#\r\n# This example has a standalone node ready to go except for possibly changing\r\n# the sniffing interface.\r\n\r\n# This is a complete standalone configuration.  Most likely you will\r\n# only need to change the interface.\r\n[bro]\r\ntype=standalone\r\nhost=localhost\r\ninterface=eth0\r\n\r\n## Below is an example clustered configuration. If you use this,\r\n## remove the [bro] node above.\r\n\r\n#[logger]\r\n#type=logger\r\n#host=localhost\r\n#\r\n#[manager]\r\n#type=manager\r\n#host=localhost\r\n#\r\n#[proxy-1]\r\n#type=proxy\r\n#host=localhost\r\n#\r\n#[worker-1]\r\n#type=worker\r\n#host=localhost\r\n#interface=eth0\r\n#\r\n#[worker-2]\r\n#type=worker\r\n#host=localhost\r\n#interface=eth0",
                                                                      "networks_cfg": "/usr/local/bro/etc/networks.cfg",
                                                                      "networks_cfg_text": "# List of local networks in CIDR notation, optionally followed by a\r\n# descriptive tag.\r\n# For example, \"10.0.0.0/8\" or \"fe80::/64\" are valid prefixes.\r\n\r\n10.0.0.0/8          Private IP space\r\n172.16.0.0/12       Private IP space\r\n192.168.0.0/16      Private IP space",
                                                                      "local_bro": "/usr/local/bro/share/bro/site/local.bro",
                                                                      "local_bro_text": "##! Local site policy. Customize as appropriate.\r\n##!\r\n##! This file will not be overwritten when upgrading or reinstalling!\r\n\r\n# This script logs which scripts were loaded during each run.\r\n@load misc/loaded-scripts\r\n\r\n# Apply the default tuning scripts for common tuning settings.\r\n@load tuning/defaults\r\n\r\n# Estimate and log capture loss.\r\n@load misc/capture-loss\r\n\r\n# Enable logging of memory, packet and lag statistics.\r\n@load misc/stats\r\n\r\n# Load the scan detection script.\r\n@load misc/scan\r\n\r\n# Detect traceroute being run on the network. This could possibly cause\r\n# performance trouble when there are a lot of traceroutes on your network.\r\n# Enable cautiously.\r\n#@load misc/detect-traceroute\r\n\r\n# Generate notices when vulnerable versions of software are discovered.\r\n# The default is to only monitor software found in the address space defined\r\n# as \"local\".  Refer to the software framework's documentation for more\r\n# information.\r\n@load frameworks/software/vulnerable\r\n\r\n# Detect software changing (e.g. attacker installing hacked SSHD).\r\n@load frameworks/software/version-changes\r\n\r\n# This adds signatures to detect cleartext forward and reverse windows shells.\r\n@load-sigs frameworks/signatures/detect-windows-shells\r\n\r\n# Load all of the scripts that detect software in various protocols.\r\n@load protocols/ftp/software\r\n@load protocols/smtp/software\r\n@load protocols/ssh/software\r\n@load protocols/http/software\r\n# The detect-webapps script could possibly cause performance trouble when\r\n# running on live traffic.  Enable it cautiously.\r\n#@load protocols/http/detect-webapps\r\n\r\n# This script detects DNS results pointing toward your Site::local_nets\r\n# where the name is not part of your local DNS zone and is being hosted\r\n# externally.  Requires that the Site::local_zones variable is defined.\r\n@load protocols/dns/detect-external-names\r\n\r\n# Script to detect various activity in FTP sessions.\r\n@load protocols/ftp/detect\r\n\r\n# Scripts that do asset tracking.\r\n@load protocols/conn/known-hosts\r\n@load protocols/conn/known-services\r\n@load protocols/ssl/known-certs\r\n\r\n# This script enables SSL/TLS certificate validation.\r\n@load protocols/ssl/validate-certs\r\n\r\n# This script prevents the logging of SSL CA certificates in x509.log\r\n@load protocols/ssl/log-hostcerts-only\r\n\r\n# Uncomment the following line to check each SSL certificate hash against the ICSI\r\n# certificate notary service; see http://notary.icsi.berkeley.edu .\r\n# @load protocols/ssl/notary\r\n\r\n# If you have libGeoIP support built in, do some geographic detections and\r\n# logging for SSH traffic.\r\n@load protocols/ssh/geo-data\r\n# Detect hosts doing SSH bruteforce attacks.\r\n@load protocols/ssh/detect-bruteforcing\r\n# Detect logins using \"interesting\" hostnames.\r\n@load protocols/ssh/interesting-hostnames\r\n\r\n# Detect SQL injection attacks.\r\n@load protocols/http/detect-sqli\r\n\r\n#### Network File Handling ####\r\n\r\n# Enable MD5 and SHA1 hashing for all files.\r\n@load frameworks/files/hash-all-files\r\n\r\n# Detect SHA1 sums in Team Cymru's Malware Hash Registry.\r\n@load frameworks/files/detect-MHR\r\n\r\n# Uncomment the following line to enable detection of the heartbleed attack. Enabling\r\n# this might impact performance a bit.\r\n# @load policy/protocols/ssl/heartbleed\r\n\r\n# Uncomment the following line to enable logging of connection VLANs. Enabling\r\n# this adds two VLAN fields to the conn.log file.\r\n# @load policy/protocols/conn/vlan-logging\r\n\r\n# Uncomment the following line to enable logging of link-layer addresses. Enabling\r\n# this adds the link-layer address for each connection endpoint to the conn.log file.\r\n# @load policy/protocols/conn/mac-logging\r\n\r\n# Uncomment the following line to enable the SMB analyzer.  The analyzer\r\n# is currently considered a preview and therefore not loaded by default.\r\n# @load policy/protocols/smb\r\n\r\n# Not modify this lines ! (useful for ProbeManager)\r\n@load myscripts\r\n@load-sigs mysignatures"
                                                                      }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(' was added successfully', str(response.content))
        self.assertIn('Test configuration OK', str(response.content))
        response = self.client.post('/admin/bro/configuration/add/', {'name': 'conftest-false',
                                                                          'conf_rules_directory': '/etc/bro/rules',
                                                                          'conf_script_directory': '/etc/bro/lua',
                                                                          'conf_iprep_directory': '/etc/bro/iprep',
                                                                          'conf_file': '/etc/bro/bro.yaml',
                                                                          }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(' was added successfully', str(response.content))
        self.assertIn('Test configuration OK', str(response.content))
        self.assertEqual(len(Configuration.get_all()), 4)
        response = self.client.post('/admin/bro/configuration/', {'action': 'test_configurations',
                                                                      '_selected_action': '2'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test configurations OK", str(response.content))
        # Conf failed
        response = self.client.post('/admin/bro/configuration/add/', {'name': 'conftest-failed',
                                                                          'conf_rules_directory': '/etc/bro/rules',
                                                                          'conf_script_directory': '/etc/bro/lua',
                                                                          'conf_iprep_directory': '/etc/bro/iprep',
                                                                          'conf_file': '/etc/bro/bro.yaml',
                                                                          'conf_advanced': True,
                                                                          'conf_advanced_text': "FAILED",
                                                                          'conf_HOME_NET': "[192.168.0.0/24]",
                                                                          'conf_EXTERNAL_NET': "!$HOME_NET",
                                                                          'conf_HTTP_SERVERS': "$HOME_NET",
                                                                          'conf_SMTP_SERVERS': "$HOME_NET",
                                                                          'conf_SQL_SERVERS': "$HOME_NET",
                                                                          }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(' was added successfully', str(response.content))
        self.assertIn('Test configuration failed !', str(response.content))
        self.assertEqual(len(Configuration.get_all()), 5)
        response = self.client.post('/admin/bro/configuration/', {'action': 'test_configurations',
                                                                      '_selected_action': '5'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test configurations failed !", str(response.content))