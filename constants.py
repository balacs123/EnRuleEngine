import os

log_path = os.getcwd()

log_file_name = log_path + os.path.sep + 'monitor_cli.log'
history_file = log_path + os.path.sep + '.monitor_history'
cli_settings_file = log_path + os.path.sep + '.monitor_cli_settings.json'

header_lines = ['Name', 'Path', 'Tags']

add_data_cargs = ['--signal', '--value', '--value_type']
add_datafile_cargs = ['--path', '--filename']
add_rule_cargs = ['--signal', '--value_type', '--conditions', '--value']
value_type_ar = ['Integer', 'String', 'DateTime']

history_length = 1000
