#!/usr/bin/env python
#encoding:utf-8
from __future__ import unicode_literals
from __future__ import print_function

import os,sys,inspect
import mock
import __builtin__
import tempfile
import unittest

DIRECTORY = 'tests'
filename_pattern = '{0}/test_{1}.py'
original_input = __builtin__.raw_input
original_print = __builtin__.print
saved_input = []

pattern='''#!/usr/bin/env python
#encoding:utf-8
from __future__ import unicode_literals
from __future__ import print_function

from mock import *
import unittest
import __builtin__

class Test_{0}(unittest.TestCase):
	@patch("__builtin__.raw_input",create=True,side_effect={1})
	@patch("__builtin__.print",create=True)
	def test_{0}(self,myMockPrint,mock_input):
		expected = {2}
		cmds = {3}
		expected_ex = {4}
		for key,item in enumerate(cmds):
			try:
				eval(item)
			except AssertionError as ex:
				raise ex
			except Exception as ex:
				self.assertEqual(type(expected_ex[key]).__name__, type(ex).__name__)
				self.assertEqual(expected_ex[key].args[0], ex.args[0])
			self.assertEqual(myMockPrint.mock_calls,expected[key])
			myMockPrint.reset_mock()
'''

def myInput(prompt=''):
	global saved_input
	result = original_input(prompt)
	saved_input.append(result)
	return result

def get_cmd():
	global saved_input
	cmds = []
	exceptions= []
	saved_print = []
	saved_input = []
	print("Run commands: (type Ctrl+D to finish)")
	while True:
		with mock.patch("__builtin__.raw_input",create=True,side_effect=myInput)as mock_input:
			with mock.patch("__builtin__.print",create=True,side_effect=print) as myMockPrint:
				try:
					cmd = original_input('> ')
					cmds.append(cmd)
					exec(cmd)
					exceptions.append(None)
					saved_print.append(myMockPrint.mock_calls)
					if len(cmds)>len(saved_input):
						saved_input.append(None)
				except EOFError:
					return (cmds,exceptions,saved_input,saved_print)
				except Exception as ex:
					tpl = "  {0}^\n{1}:{2}"
					indent = ' '*(ex.args[1][2]-1) if len(ex.args)>1 else ''
					msg_name = type(ex).__name__
					msg_details = ex.args[0]
					message = tpl.format(indent,msg_name,msg_details)
					original_print(message)
					exceptions.append(ex)
					saved_print.append(myMockPrint.mock_calls)
					if len(cmds)>len(saved_input):
						saved_input.append(None)
						
def dry_run(scenario):
	original_print('\nBuilding test script...')
	(osd,tmpFile) = tempfile.mkstemp(dir='.',suffix='.py')
	with open(tmpFile,'w') as fd:
		fd.write(pattern.format('tmp',scenario[2],scenario[3],scenario[0],scenario[1]))
		fd.close()
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
	while title is None or os.path.isfile(DIRECTORY+'/'+title):
		if title is not None:
			original_print('{0} already exists'.format(title))
		original_print('OK, please indicate a name for your test:')
		title = original_input('>')
	return title
	
def check_dir():
	if not os.path.isdir(DIRECTORY):
		os.mkdir(DIRECTORY)

if __name__ == '__main__':
	check_dir()
	scenario = get_cmd()
	dry_run(scenario)
	title = choose_name()
	with open(filename_pattern.format(DIRECTORY,title),'w') as fd:
		fd.write(pattern.format(title,scenario[2],scenario[3],scenario[0],scenario[1]))
	original_print('Test script saved in test_'+title)
	original_print('Just type `\033[1mpython -m unittest {1}.test_{0}\033[0m` in order execute it.'.format(title,DIRECTORY))
	original_print('Otherwise `\033[1mpython -m unittest discover\033[0m` in order execute all tests in subdirectories.')
	
