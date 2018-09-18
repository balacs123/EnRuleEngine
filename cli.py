import cmd
import shlex
import readline
import json
from datetime import datetime
from constants import *


class ruleEngine_cli(cmd.Cmd):
    def __init__(self, **kwargs):
        cmd.Cmd.__init__(self, **kwargs)
        self.intro = '#Click ctrl+C to exit #\n'
        self.prompt = '$ '

        self.node_info_dict = {}
        self.nodes = []

        self.load_cli_settings()
        self.get_all_cmd_info()

        readline.read_history_file(history_file)
        readline.set_history_length(history_length)

    def load_cli_settings(self):
        if not os.path.isfile(log_file_name):
             with open(log_file_name, 'w') as fp:
                  pass

        if not os.path.isfile(history_file):
            with open(history_file, 'w') as fp:
                 pass

        return

    def set_cli_settings(self, **kwargs):
        with open(cli_settings_file, 'r') as fp:
            line = fp.readline()

        settings_dict = json.loads(line)
        for set_key, set_val in kwargs.items():
            settings_dict[set_key] = set_val

        with open(cli_settings_file, 'w') as fp:
            fp.write(json.dumps(settings_dict))

        return


    def get_all_cmd_info(self):
        self.all_cmd_dict = {
                            'add':{
                                'data_stream': {
                                        add_data_cargs[0]:{
                                        add_data_cargs[1]:{
                                        add_data_cargs[2]:{
                                        }}}
                                        },
                                'datafile': {
                                        add_datafile_cargs[0]:{
                                        add_datafile_cargs[1]:{
                                        }}
                                        },
                                'rule': {
                                        add_rule_cargs[0]:{
                                        add_rule_cargs[1]:{
                                        add_rule_cargs[2]:{
                                        add_rule_cargs[3]:{
                                        }}}}
                                        },
                                    },
                            'show':{
                                'rules': { }
                                },
                                }
        return

    def write_to_log(self):
        with open(log_file_name, 'a') as fp:
            if readline.get_current_history_length():
                fp.write(str(datetime.now()) + '\t' + readline.get_history_item(readline.get_current_history_length()) + '\n')
 
    def common_complete(self, text, line, begidx, endidx):
        line_cmds = shlex.split(line)
        ccmd = line_cmds[0]
        if (len(line_cmds) > 2):
            if ('--' in line_cmds[-1]) and ('--' in line_cmds[-2]):
                return []

        c_dict = self.all_cmd_dict.get(ccmd, {})
        prev_dict = c_dict
        org_line_cmds = line_cmds[:]
        if '--' in line:
            new_line_cmds = []
            st_kw = 0
            for cmd in line_cmds:
                if ('--' not in cmd) and (not st_kw):
                    new_line_cmds.append(cmd)
                if '--' in cmd:
                    st_kw = 1
                    new_line_cmds.append(cmd)
            line_cmds = new_line_cmds 
           
        for cmd in line_cmds[:]:
            if ccmd == cmd:continue
            prev_dict = c_dict
            c_dict = c_dict.get(cmd, {})
            if not c_dict:
                break

        prev_cmds = prev_dict.keys()
        if not text:
            if (line_cmds[-1] in prev_cmds) and c_dict:
                completions = [f for f in c_dict.keys() if f.startswith(text)]
            else:
                if (line_cmds[-1] in prev_cmds) or ('--' in org_line_cmds[-1]):
                    completions = []
                else:
                    completions = prev_cmds
        elif line_cmds[-2] in prev_cmds:
            completions = [f for f in c_dict.keys() if f.startswith(text)]
        else:
            completions = [f for f in prev_cmds if f.startswith(text)]

        if '--' in org_line_cmds[-1]:
             completions = [x for x in completions if '--' not in x]

        completions = [x+' ' for x in completions]
        return completions

    def do_add(self, arguments):
        'Add a Directory/Tags.\nUsage: add directories/tags ..'
        usage = self.do_add.__doc__.split('\n')[1]
        args = shlex.split(arguments)
        if not args:
            print usage
            return
        if 'data_stream' == args[0]:
            self.add_data_stream(args[1:])
        elif 'datafile' == args[0]:
            self.add_datafile(args[1:])
        elif 'rule' == args[0]:
            self.add_rules(args[1:])
        else:
            print usage

    def complete_add(self, text, line, begidx, endidx):
        completions = self.common_complete(text, line, begidx, endidx)
        if (not text and (line.split()[-1] == '--value_type')):
            completions = [f+' ' for f in value_type_ar]
        elif (text and (line.split()[-2] == '--value_type')):
            completions = [f+' ' for f in value_type_ar if f.startswith(text)]
        return completions

    def add_data_stream(self, args):
        'Add a Data stream.\n'
        usage = 'add data_stream <signal> <value> <value_type>\n\tOr\n'
        usage += 'add directory --signal <signal> --value <value> --value_type <type>'
        org_args = args[:]
        cargs = [x for x in args if '--' in x]
        args = [x for x in args if '--' not in x]
        missed_args = set(add_data_cargs) - set(cargs)
        if org_args and org_args[-1] in 'help':
            print usage
        elif len(args) >= len(add_data_cargs) and (not missed_args or len(missed_args) == len(add_data_cargs)):
            signal, value, val_type = args[:3]
            rfile = open("rules_file.txt", "r")
            lines = rfile.readlines()
            rfile.close()
            for line in lines:
                line = line.split(',')
                if signal == line[0] and val_type == line[1]:
                    res = self.conditions_check(value, line)
                    if res:
                        print signal

    def conditions_check(self, value, line):
        if "Integer" in line[1]:
            if "notgreater" in line[2]:
                if value > line[3]:
                    return True
            elif "notlesser" in line[2]:
                if value < line[3]:
                    return True
            elif "notequal" in line[2]:
                if value == line[3]:
                    return True
            elif "greater" in line[2]:
                if value < line[3]:
                    return True
            elif "lesser" in line[2]:
                if value > line[3]:
                    return True
            elif "equal" in line[2]:
                if value == line[3]:
                    return True
            else:
                return False
        elif "String" in line[1]:
            if "notin" in line[2]:
                if value in line[3]:
                    return True
            elif "bein" in line[2]:
                if value not in line[3]:
                    return True
            else:
                return False
        elif "DateTime" in line[1]:
            value = datetime.strptime(value, "%d/%m/%Y %H:%M:%S.%f")
            if "currentTime" in line[3]:
                line[3] = datetime.now()
            else:
                line[3] = datetime.strptime(line[3], "%d/%m/%Y %H:%M:%S.%f")

            if "notgreater" in line[2]:
                if value > line[3]:
                    return True
            elif "notlesser" in line[2]:
                if value < line[3]:
                    return True
            elif "notequal" in line[2]:
                if value == line[3]:
                    return True
            elif "greater" in line[2]:
                if value < line[3]:
                    return True
            elif "lesser" in line[2]:
                if value > line[3]:
                    return True
            elif "equal" in line[2]:
                if value == line[3]:
                    return True
            else:
                return False
    
    def add_datafile(self, args):
        'Add datafile.'
        usage = 'Usage: add datafile <path> <filename>\n\tOr\n'
        usage += 'Usage: add datafile --path <path> --filename <filename>'
        org_args = args[:]
        cargs = [x for x in args if '--' in x]
        args = [x for x in args if '--' not in x]
        missed_args = set(add_datafile_cargs) - set(cargs)
        if org_args and org_args[-1] in 'help':
            print usage
        elif len(args) >= len(add_datafile_cargs) and (not missed_args or len(missed_args) == len(add_datafile_cargs)):
            path, filename = args[:2]
            filepath = os.path.join(path, filename)
            with open(filepath) as f:
                file_data = json.load(f)
            for item in file_data:
                rfile = open("rules_file.txt", "r")
                lines = rfile.readlines()
                rfile.close()
                for line in lines:
                    line = line.split(',')
                    if item["signal"] == line[0] and item["value_type"] == line[1]:
                        if item["value_type"] == "Integer":
                            item["value"] = float(item["value"])
                        res = self.conditions_check(item["value"], line)
                        if res:
                            print item["signal"]

        else:
            print usage
        self.write_to_log()

    def add_rules(self, args):
        'Add a Rule.\n'
        usage = 'add rule <signal> <conditions> <value>\n\tOr\n'
        usage += 'add rule --signal <signale> --conditions <conditions> --value <value>'
        org_args = args[:]
        cargs = [x for x in args if '--' in x]
        args = [x for x in args if '--' not in x]
        missed_args = set(add_rule_cargs) - set(cargs)
        if org_args and org_args[-1] in 'help':
            print usage
        elif len(args) >= len(add_rule_cargs) and (not missed_args or len(missed_args) == len(add_rule_cargs)):
            signal, value_type, conditions, value = args[:4]
            fp = open("rules_file.txt","a+")
            line = signal + ',' + value_type + ',' + conditions + ',' + value + '\n'
            fp.write(line)
            fp.close()
        else:
            print usage
        self.write_to_log()

    def do_show(self, arguments = []):
        'Show Details directory.\nUsage: show nodes/node/logs/server_ip/http_timeout/summary ...'
        usage = self.do_show.__doc__.split('\n')[1]
        args = shlex.split(arguments)
        if not args:
            print usage
            return
        if 'rules' == args[0]:
            self.show_rules()
        else:
            print usage
    
    def complete_show(self, text, line, begidx, endidx):
        completions = self.common_complete(text, line, begidx, endidx)
        return completions


    def show_rules(self):
        'Show Directory Details.'
        usage = 'Usage: show rules\n'
        fp = open("rules_file.txt", "r")
        lines = fp.readlines()
        for line in lines:
            print line

if __name__ == '__main__':
    ruleEngine_cli().cmdloop()
