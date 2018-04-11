import glob
import logging
import os
import re
import subprocess
from collections import OrderedDict

import select2.fields
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from core.models import Probe, ProbeConfiguration
from core.ssh import execute, execute_copy
from rules.models import RuleSet, Rule

logger = logging.getLogger(__name__)


class Configuration(ProbeConfiguration):
    """
    Configuration for Bro IDS, Allows you to reuse the configuration.
    """
    probeconfiguration = models.OneToOneField(ProbeConfiguration, parent_link=True, related_name='bro_configuration',
                                              on_delete=models.CASCADE, editable=False)
    with open(settings.BASE_DIR + "/bro/default-broctl.cfg", encoding='utf_8') as f:
        BROCTL_DEFAULT = f.read()
    with open(settings.BASE_DIR + "/bro/default-networks.cfg", encoding='utf_8') as f:
        NETWORKS_DEFAULT = f.read()
    with open(settings.BASE_DIR + "/bro/default-node.cfg", encoding='utf_8') as f:
        NODE_DEFAULT = f.read()
    with open(settings.BASE_DIR + "/bro/default-local.bro", encoding='utf_8') as f:
        LOCAL_DEFAULT = f.read()
    my_scripts = models.CharField(max_length=400, default="/usr/local/bro/share/bro/site/myscripts.bro",
                                  editable=False)
    my_signatures = models.CharField(max_length=400, default="/usr/local/bro/share/bro/site/mysignatures.sig",
                                     editable=False)
    policydir = models.CharField(max_length=400, default="/usr/local/bro/share/bro/policy/")
    bin_directory = models.CharField(max_length=800, default="/usr/local/bro/bin/")
    broctl_cfg = models.CharField(max_length=400, default="/usr/local/bro/etc/broctl.cfg")
    broctl_cfg_text = models.TextField(default=BROCTL_DEFAULT)
    node_cfg = models.CharField(max_length=400, default="/usr/local/bro/etc/node.cfg")
    node_cfg_text = models.TextField(default=NODE_DEFAULT)
    networks_cfg = models.CharField(max_length=400, default="/usr/local/bro/etc/networks.cfg")
    networks_cfg_text = models.TextField(default=NETWORKS_DEFAULT)
    local_bro = models.CharField(max_length=400, default="/etc/bro/site/local.bro")
    local_bro_text = models.TextField(default=LOCAL_DEFAULT)

    def __str__(self):
        return self.name

    def test(self):  # TODO Not yet implemented
        pass


class SignatureBro(Rule):
    """
    Stores a signature Bro compatible. (pattern matching), see https://www.bro.org/sphinx/frameworks/signatures.html
    """
    msg = models.CharField(max_length=1000, unique=True)
    pcap_success = models.FileField(name='pcap_success', upload_to='pcap_success', blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sid = self.id

    def __str__(self):
        return str(self.sid) + " : " + str(self.msg)

    @classmethod
    def get_by_sid(cls, sid):
        try:
            obj = cls.objects.get(sid=sid)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + str(e))
            return None
        return obj

    @classmethod
    def get_by_msg(cls, msg):
        try:
            obj = cls.objects.get(msg=msg)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + str(e))
            return None
        return obj

    @classmethod
    def find(cls, pattern):
        """Search the pattern in all the signatures"""
        return cls.objects.filter(rule_full__contains=pattern)

    @classmethod
    def extract_signature_attributs(cls, line, rulesets=None):
        getmsg = re.compile("event *\"(.*?)\"")
        try:
            match = getmsg.search(line)
            if match:
                if SignatureBro.get_by_msg(match.groups()[0]):
                    signature = cls.get_by_msg(match.groups()[0])
                    signature.updated_date = timezone.now()
                else:
                    signature = SignatureBro()
                    signature.created_date = timezone.now()
                signature.rule_full = line
                signature.save()
                if rulesets:
                    for ruleset in rulesets:
                        ruleset.signatures.add(signature)
                        ruleset.save()
                return "rule saved : " + str(signature.sid)
        except:
            return "rule not saved"

    def test(self):
        with self.get_tmp_dir("test_sig") as tmp_dir:
            rule_file = tmp_dir + str(self.sid) + ".sig"
            with open(rule_file, 'w') as f:
                f.write(self.rule_full)
            cmd = [settings.BRO_BINARY,
                   '-a', '-S',
                   '-s', rule_file
                   ]
            process = subprocess.Popen(cmd, cwd=tmp_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (outdata, errdata) = process.communicate()
            logger.debug(outdata)
            # if success ok
            if "Error in signature" in outdata:
                return {'status': False, 'errors': errdata}
            else:
                return {'status': True}

    def test_pcap(self):
        with self.get_tmp_dir("test_pcap") as tmp_dir:
            rule_file = tmp_dir + "signature.txt"
            with open(rule_file, 'w', encoding='utf_8') as f:
                f.write(self.rule_full)
            cmd = [settings.BRO_BINARY + "bro",
                   '-r', settings.BASE_DIR + "/" + self.pcap_success.name,
                   '-s', rule_file
                   ]
            process = subprocess.Popen(cmd, cwd=tmp_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (outdata, errdata) = process.communicate()
            logger.debug(outdata)
            test = False
            if os.path.isfile(tmp_dir + "signatures.log"):
                with open(tmp_dir + "signatures.log", "r", encoding='utf_8') as f:
                    if self.msg in f.read():
                        test = True
            # if success ok
        if process.returncode == 0 and test:
            return {'status': True}
            # if not -> return error
        errdata += b"Alert not generated"
        return {'status': False, 'errors': errdata}


class ScriptBro(Rule):
    """
    Stores a script Bro compatible. see : https://www.bro.org/sphinx/scripting/index.html#understanding-bro-scripts
    """
    name = models.CharField(max_length=100, unique=True)
    pcap_success = models.FileField(name='pcap_success', upload_to='pcap_success', blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def find(cls, pattern):
        """Search the pattern in all the scripts"""
        return cls.objects.filter(rule_full__contains=pattern)

    @classmethod
    def extract_script_attributs(cls, file, rulesets=None):  # TODO Not yet implemented
        pass

    def test(self):
        with self.get_tmp_dir("test_script") as tmp_dir:
            rule_file = tmp_dir + str(self.id) + ".bro"
            with open(rule_file, 'w') as f:
                f.write(self.rule_full)
            cmd = [settings.BRO_BINARY,
                   '-a', '-S',
                   '-s', rule_file
                   ]
            process = subprocess.Popen(cmd, cwd=tmp_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (outdata, errdata) = process.communicate()
            logger.debug(outdata)
            # if success ok
            if "Error in script" in outdata:
                return {'status': False, 'errors': errdata}
            else:
                return {'status': True}

    def test_pcap(self):
        with self.get_tmp_dir("test_pcap") as tmp_dir:
            rule_file = tmp_dir + "script.txt"
            with open(rule_file, 'w', encoding='utf_8') as f:
                f.write(self.rule_full)
            cmd = [settings.BRO_BINARY + "bro",
                   '-r', settings.BASE_DIR + "/" + self.pcap_success.name,
                   '-s', rule_file
                   ]
            process = subprocess.Popen(cmd, cwd=tmp_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (outdata, errdata) = process.communicate()
            logger.debug(outdata)
            test = False
            if os.path.isfile(tmp_dir + "notice.log"):
                with open(tmp_dir + "notice.log", "r", encoding='utf_8') as f:
                    if self.name in f.read():
                        test = True
            # if success ok
        if process.returncode == 0 and test:
            return {'status': True}
            # if not -> return error
        errdata += b"Alert not generated"
        return {'status': False, 'errors': errdata}


class RuleSetBro(RuleSet):
    """Set of signatures and scripts Bro compatible"""
    signatures = select2.fields.ManyToManyField(SignatureBro,
                                                blank=True,
                                                ajax=True,
                                                search_field=lambda q: Q(sid__icontains=q),
                                                sort_field='sid',
                                                js_options={'quiet_millis': 200}
                                                )
    scripts = select2.fields.ManyToManyField(ScriptBro,
                                             blank=True,
                                             ajax=True,
                                             search_field=lambda q: Q(sid__icontains=q) | Q(name__icontains=q),
                                             sort_field='sid',
                                             js_options={'quiet_millis': 200}
                                             )

    def __str__(self):
        return self.name


class Bro(Probe):
    """
    Stores an instance of Bro IDS software. Configuration settings.
    """
    rulesets = models.ManyToManyField(RuleSetBro, blank=True)
    configuration = models.ForeignKey(Configuration, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = self.__class__.__name__

    def __str__(self):
        return self.name + " : " + self.description

    def install(self, version="2.5.3"):
        if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
            command1 = "apt update"
            command2 = "apt install cmake make gcc g++ flex bison libpcap-dev libssl1.0-dev python-dev swig " \
                       "zlib1g-dev libmagic-dev libgeoip-dev sendmail libcap2-bin " \
                       "wget curl ca-certificates "
            command3 = "wget https://www.bro.org/downloads/bro-" + version + ".tar.gz"
            command4 = "tar xf bro-" + version + ".tar.gz"
            command5 = "( cd bro-" + version + " && ./configure )"
            command6 = "( cd bro-" + version + " && make -j$(nproc) )"
            command7 = "( cd bro-" + version + " && make install )"
            command8 = "rm bro-" + version + ".tar.gz && rm -rf bro-" + version
            command9 = "export PATH=/usr/local/bro/bin:$PATH && export LD_LIBRARY_PATH=/usr/local/bro/lib/"
        else:
            raise Exception("Not yet implemented")
        tasks_unordered = {"1_update_repo": command1,
                           "2_install_dep": command2,
                           "3_download": command3,
                           "4_tar": command4,
                           "5_configure": command5,
                           "6_make": command6,
                           "7_make_install": command7,
                           "8_rm": command8,
                           "9_export": command9}
        tasks = OrderedDict(sorted(tasks_unordered.items(), key=lambda t: t[0]))
        try:
            response = execute(self.server, tasks, become=True)
            self.installed = True
            self.save()
        except Exception as e:
            logger.exception('install failed')
            return {'status': False, 'errors': str(e)}
        logger.debug("output : " + str(response))
        return {'status': True}

    def update(self):
        return self.install()

    def start(self):
        if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
            command = settings.BROCTL_BINARY + " start"
        else:  # pragma: no cover
            raise Exception("Not yet implemented")
        tasks = {"start": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception:
            logger.exception("Error during start")
            return {'status': False, 'errors': "Error during start"}
        logger.debug("output : " + str(response))
        return {'status': True}

    def stop(self):
        if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
            command = settings.BROCTL_BINARY + " stop"
        else:  # pragma: no cover
            raise Exception("Not yet implemented")
        tasks = {"stop": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception:
            logger.exception("Error during stop")
            return {'status': False, 'errors': "Error during stop"}
        logger.debug("output : " + str(response))
        return {'status': True}

    def status(self):
        if self.installed:
            if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
                command = settings.BROCTL_BINARY + " status"
            else:  # pragma: no cover
                raise Exception("Not yet implemented")
            tasks = {"status": command}
            try:
                response = execute(self.server, tasks, become=True)
            except Exception:
                logger.exception('Failed to get status')
                return 'Failed to get status'
            logger.debug("output : " + str(response))
            return response['status']
        else:
            return " "

    def reload(self):
        if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
            command = settings.BROCTL_BINARY + " deploy"
        else:  # pragma: no cover
            raise Exception("Not yet implemented")
        tasks = {"reload": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception:
            logger.exception("Error during reload")
            return {'status': False, 'errors': "Error during reload"}
        logger.debug("output : " + str(response))
        return {'status': True}

    def restart(self):
        if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
            command1 = settings.BROCTL_BINARY + " stop"
            command2 = settings.BROCTL_BINARY + " start"
        else:  # pragma: no cover
            raise Exception("Not yet implemented")
        tasks_unordered = {"1_stop": command1,
                           "2_start": command2}
        tasks = OrderedDict(sorted(tasks_unordered.items(), key=lambda t: t[0]))
        try:
            response = execute(self.server, tasks, become=True)
        except Exception:
            logger.exception("Error during restart")
            return {'status': False, 'errors': "Error during restart"}
        logger.debug("output : " + str(response))
        return {'status': True}

    def test_rules(self):
        test = True
        errors = list()
        for ruleset in self.rulesets.all():
            for signature in ruleset.signatures.all():
                response = signature.test()
                if not response['status']:
                    test = False
                    errors.append(str(response['errors']))
        if test:
            return {'status': True}
        else:
            return {'status': False, 'errors': errors}

    def deploy_rules(self):
        deploy = True
        response = dict()
        errors = list()
        value_signatures = ""
        value_scripts = ""
        for ruleset in self.rulesets.all():
            for signature in ruleset.signatures.all():
                if signature.enabled:
                    value_signatures += signature.rule_full + os.linesep
            for script in ruleset.scripts.all():
                if script.enabled:
                    value_scripts += script.rule_full + os.linesep
        with self.get_tmp_dir(self.pk) as tmp_dir:
            with open(tmp_dir + "signatures.txt", 'w', encoding='utf_8') as f:
                f.write(value_signatures)
            try:
                response = execute_copy(self.server, src=tmp_dir + 'signatures.txt',
                                        dest=self.configuration.my_signatures,
                                        become=True)
            except Exception as e:
                logger.exception('excecute_copy failed')
                deploy = False
                errors.append(str(e))
            with open(tmp_dir + "scripts.txt", 'w', encoding='utf_8') as f:
                f.write(value_scripts)
            try:
                response = execute_copy(self.server, src=tmp_dir + 'scripts.txt',
                                        dest=self.configuration.my_scripts,
                                        become=True)
            except Exception as e:
                logger.exception('excecute_copy failed')
                deploy = False
                errors.append(str(e))
            logger.debug("output : " + str(response))
        result = self.reload()
        if deploy and result['status']:
            self.rules_updated_date = timezone.now()
            self.save()
            return {"status": deploy}
        else:
            return {'status': deploy, 'errors': errors}

    def deploy_conf(self):
        with self.get_tmp_dir(self.pk) as tmp_dir:
            with open(tmp_dir + "broctl_cfg.conf", 'w', encoding='utf_8') as f:
                f.write(self.configuration.broctl_cfg_text)
            with open(tmp_dir + "node_cfg.conf", 'w', encoding='utf_8') as f:
                f.write(self.configuration.node_cfg_text)
            with open(tmp_dir + "networks_cfg.conf", 'w', encoding='utf_8') as f:
                f.write(self.configuration.networks_cfg_text)
            with open(tmp_dir + "local_bro.conf", 'w', encoding='utf_8') as f:
                f.write(self.configuration.local_bro_text)
            deploy = True
            errors = list()
            response = dict()
            try:
                response = execute_copy(self.server, src=os.path.abspath(tmp_dir + 'broctl_cfg.conf'),
                                        dest=self.configuration.broctl_cfg, become=True)
                response = execute_copy(self.server, src=os.path.abspath(tmp_dir + 'node_cfg.conf'),
                                        dest=self.configuration.node_cfg, become=True)
                response = execute_copy(self.server, src=os.path.abspath(tmp_dir + 'networks_cfg.conf'),
                                        dest=self.configuration.networks_cfg, become=True)
                response = execute_copy(self.server, src=os.path.abspath(tmp_dir + 'local_bro.conf'),
                                        dest=self.configuration.local_bro, become=True)
            except Exception as e:
                logger.exception('deploy conf failed')
                deploy = False
                errors.append(str(e))
            logger.debug("output : " + str(response))
        if deploy:
            return {'status': deploy}
        else:
            return {'status': deploy, 'errors': errors}
