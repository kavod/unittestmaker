#!/usr/bin/env python
#encoding:utf-8
from __future__ import unicode_literals
from __future__ import print_function

import os,sys,inspect
import mock
import __builtin__
import tempfile
import unittest
import copy
import string
import random

DIRECTORY = 'tests'
filename_pattern = '{0}/test_{1}.py'
original_input = __builtin__.raw_input
original_print = __builtin__.print
local_vars = {}
local_vars['saved_input'] = []

pattern_cmd_no_except = """		with patch("__builtin__.raw_input",create=True,side_effect={2})as mock_input:
			{0}
			self.assertEqual(myMockPrint.mock_calls,{1})
			myMockPrint.reset_mock()
"""

pattern_cmd_except = """		with patch("__builtin__.raw_input",create=True,side_effect={2})as mock_input:
			with self.assertRaises({3}):
				{0}
			self.assertEqual(myMockPrint.mock_calls,{1})
			myMockPrint.reset_mock()
"""

global_pattern = '''#!/usr/bin/env python
#encoding:utf-8
from __future__ import unicode_literals
from __future__ import print_function

from mock import *
import unittest
import __builtin__

class Test_{0}(unittest.TestCase):
	@patch("__builtin__.print",create=True)
	def test_{0}(self,myMockPrint):
{1}
'''

def var_generator():
	return ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(16))		
	
sub_vars = {
			'local_vars':var_generator(),
			'local_func':var_generator(),
			'mock_input':var_generator(),
			'myMockPrint':var_generator()
			}
			
def substitute_vars(str):
	for sub in sub_vars.keys():
		str = str.replace(sub,sub_vars[sub])
	return str


def myInput(prompt=''):
	global local_vars
	result = original_input(prompt)
	local_vars['saved_input'].append(result)
	return result

def get_cmd():
	global local_vars
	local_vars['result'] = []
	local_func = {
				'print':original_print,
				'input':original_input,
				'get_ident' : get_ident,
				'copy':copy.copy
				}
	print("Run commands: (type Ctrl+D to finish)")
	while True:
		local_vars['saved_input'] = []
		local_vars['ident'] = -1
		with mock.patch("__builtin__.raw_input",create=True,side_effect=myInput) as mock_input:
			with mock.patch("__builtin__.print",create=True,side_effect=print) as myMockPrint:
				try:
					local_vars['cmd'] = local_func['input']('>>> ')
					if local_vars['cmd'].rstrip(' \t')[-1] == ':':
						while (local_vars['ident'] != 0):
							local_vars['subcmd'] = local_func['input']('... ')
							local_vars['ident'] = local_func['get_ident'](local_vars['subcmd'])
							local_vars['cmd']+="\n" + local_vars['subcmd']
					local_vars['cmd'] = substitute_vars(local_vars['cmd'])
					exec(local_vars['cmd'])
					local_vars['cmd'] = local_vars['cmd'].replace('assert(','self.assertTrue(')
					local_vars['result'].append((local_vars['cmd'],None,local_func['copy'](local_vars['saved_input']),myMockPrint.mock_calls))
					myMockPrint.reset_mock()
				except EOFError:
					return local_vars['result']
				except Exception as ex:
					local_vars['cmd'] = local_vars['cmd'].replace('assert(','self.assertTrue(')
					local_vars['tpl'] = "  {0}^\n{1}:{2}"
					local_vars['indent'] = ' '*(ex.args[1][2]-1) if len(ex.args)>1 else ''
					local_vars['msg_name'] = type(ex).__name__
					local_vars['msg_details'] = ex.args[0]
					local_vars['message'] = local_vars['tpl'].format(local_vars['indent'],local_vars['msg_name'],local_vars['msg_details'])
					local_func['print'](local_vars['message'])
					local_vars['result'].append((local_vars['cmd'],ex,local_func['copy'](local_vars['saved_input']),myMockPrint.mock_calls))
					myMockPrint.reset_mock()

def generate_script(title,scenario):
	execution = ""
	for scenar in scenario:
		if scenar[1] is None:
			execution += pattern_cmd_no_except.format(scenar[0].replace('\n','\n\t\t\t'),scenar[3],scenar[2])
		else:
			execution += pattern_cmd_except.format(scenar[0].replace('\n','\n\t\t\t\t'),scenar[3],scenar[2],type(scenar[1]).__name__)
	return global_pattern.format(title,execution)

def build_file(title,scenario):
	original_print('\nBuilding test script...')
	if title == 'tmp':
		(osd,filename) = tempfile.mkstemp(dir='.',suffix='.py')
	else:
		filename = filename_pattern.format(DIRECTORY,title)
	with open(filename,'w') as fd:
		fd.write(generate_script('tmp',scenario))
		fd.close()
	return filename
	
def dry_run(scenario):
	tmpFile = build_file('tmp',scenario)
	"""original_print('\nBuilding test script...')
	(osd,tmpFile) = tempfile.mkstemp(dir='.',suffix='.py')
	with open(tmpFile,'w') as fd:
		fd.write(generate_script('tmp',scenario))
		fd.close()"""
	tmpName = os.path.splitext(os.path.basename(tmpFile))[0]
	tmpMod = __import__(tmpName)
	suite = unittest.TestSuite()
	suite.addTest(tmpMod.Test_tmp('test_tmp'))
	runner = unittest.TextTestRunner()
	original_print('Running test script...')
	runner.run(suite)
	os.remove(tmpFile)
	os.remove(tmpFile+'c')
	
def choose_name():
	title = None
	while title is None or title == 'tmp' or os.path.isfile(filename_pattern.format(DIRECTORY,title)):
		if title is not None:
			original_print('{0} already exists'.format(filename_pattern.format(DIRECTORY,title)))
		if title == 'tmp':
			original_print('tmp is not allowed')
		original_print('OK, please indicate a name for your test:')
		title = original_input('>')
	return title
	
def check_dir():
	if not os.path.isdir(DIRECTORY):
		os.mkdir(DIRECTORY)
	if not os.path.isfile(DIRECTORY+'/__init__.py'):
		open(DIRECTORY+'/__init__.py', 'a').close()
		
def get_ident(str):
	return len(str) - len(str.lstrip(' \t'))
	
def run():
	check_dir()
	scenario = get_cmd()
	dry_run(scenario)
	title = choose_name()
	with open(filename_pattern.format(DIRECTORY,title),'w') as fd:
		fd.write(generate_script(title,scenario))
	original_print('Test script saved in test_'+title)
	original_print('Just type `\033[1mpython -m unittest {1}.test_{0}\033[0m` in order execute it.'.format(title,DIRECTORY))
	original_print('Otherwise `\033[1mpython -m unittest discover\033[0m` in order execute all tests in subdirectories.')

if __name__ == '__main__':
	run()
