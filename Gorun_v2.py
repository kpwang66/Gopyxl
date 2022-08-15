#!/usr/bin/python
import pexpect
import sys
import time
import datetime
import re
import pickle
import pdb
import string
import subprocess
import os
import glob
from shutil import copy
from collections import namedtuple
# import httplib, urllib
from goxlsx_reader import *

# Gorun v2
# Goals: Send push notifications on progress

class Gorun(object):

	def __init__(self, session_name, goma_path = '/home/kerry/spack/opt/spack/linux-ubuntu20.04-x86_64_v4/gcc-9.4.0/goma-7.1.1-4pmbhwpvn63imkdbalyyxf5u2h4zk2r4/bin/goma', run_path = None, input_filename='input.inp', gopyxl_filename='flow.gopyxl', wait=True, interact=True, flags_dict=dict()):
		self.goma_path = goma_path
		self.curr_path = os.getcwd()
		self.input_filename = input_filename
		self.wait = wait
		self.gopyxl_filename = gopyxl_filename
		self.interact = interact
		self.flags_dict = flags_dict
		self.runID = datetime.datetime.today().strftime('%H%M%S')
		self.session_name = session_name
		self.pxlog_filename = session_name +'_'+ self.runID +'_pxlog.txt'
		self.fulllog_filename = session_name +'_'+ self.runID +'_tgplog.txt'
		self.complete = False
		self.completion_type = 'Incomplete'
		self.FEM_file_dict = Gorun.goma_mini_parser(input_filename)
		self.run_path = run_path
		self.run_time = time.time()


		# pdb.set_trace()
		run_line = goma_path + ' -i ' + input_filename
		# run_line = goma_path + ' -i ' + input_filename + ' -r .1'
		# flag_strings =  ' '.join(flags_dict)
		self.run_line = run_line + ' ' + ' '.join([key + ' ' +str(flags_dict[key]) for key in flags_dict])


		# Populate rlv_files (relevant files) using Gopyxl file if available.  Else, parse input file.
		self.rlv_files = set()
		self.rlv_files.add(input_filename)
		
		# If there is a gopyxl file, populate rlv_files with that
		if gopyxl_filename is not None:
			# from goxlsx_reader import *

			with open(gopyxl_filename, 'rb') as f:
				gopyxl = pickle.load(f)

			print("Reading: " + gopyxl_filename)
			print("gopyxl generated from: " + gopyxl.xlsx_file_info['path'] + "/" + gopyxl.xlsx_file_info['xlsx'])

			self.rlv_files.add(gopyxl_filename)
			self.rlv_files.add(gopyxl.xlsx_file_info['xlsx'])
			self.rlv_files.add(gopyxl.FEM_file_dict['SOLN file'])
			self.rlv_files.add(gopyxl.FEM_file_dict['Output EXODUS II file'])
			self.rlv_files.add(gopyxl.FEM_file_dict['FEM file'])
			self.rlv_files.add("echo_input.inp")

			# Copy the input FEM as GUESS file...basically start w a zero guess.  guess.exoII gets overwritten
			# by goma-wrapper.py if you want to load another solution
			# os.copy(gopyxl.FEM_file_dict['FEM file'], os.path,join(self.curr_path, 'guess.exoII'))
			
			for material in gopyxl.MatField_list:
				self.rlv_files.add(material.name + '.mat')
				self.rlv_files.add('echo_' + material.name + '.mat')

		# If no gopyxl file, use what we got from the mini-parser
		else:
			print('Parsing input file ' + input_filename)
			# self.FEM_file_dict = self.goma_mini_parser(input_filename)
			self.rlv_files.add(self.FEM_file_dict['FEM file'])
			self.rlv_files.add(self.FEM_file_dict['GUESS file'])
			self.rlv_files.add(self.FEM_file_dict['SOLN file'])
			self.rlv_files.add(self.FEM_file_dict['Output EXODUS II file'])

			# Copy the input FEM as GUESS file...basically start w a zero guess.  guess.exoII gets overwritten
			# by goma-wrapper.py if you want to load another solution
			# os.copy(self.FEM_file_dict['FEM file'], os.path,join(self.curr_path, 'guess.exoII'))

			mat_file_list = [f for f in os.listdir(self.curr_path) if f.endswith('.mat')]

			for mat_file in mat_file_list:
				self.rlv_files.add(mat_file)
				# rlv_files.append('echo_' + mat_file)

		print('Relevant files:')
		for filename in self.rlv_files:
			print(filename)

		# Launch Goma
		print('Running: ' + self.run_line)
		start = time.time()
		self.child = pexpect.spawnu(self.run_line, timeout=1.5, maxread=4000)
		self.child.delaybeforesend=1./20

		with open(self.pxlog_filename, 'wb') as fout:
			self.child.logfile_read = fout

			if interact==True:
				self.child.interact()

			check_progress_interval = 10
			while self.child.isalive():
				if time.time() - start > check_progress_interval:
					# Gorun.send_pushover('Progress')
					check_progress_interval = check_progress_interval + 10
				else:
					time.sleep(10)

			if wait==True:
				self.child.wait()
				self.check_complete()
			# print time.time() - start
			print('Gorun has completed (' + self.completion_type + ').  Process took ' +  str(time.time() - start) + ' seconds.')
			# Gorun.send_pushover('Gorun has completed (' + self.completion_type+ ').  Process took ' +  str(time.time() - start) + ' seconds.')

		time.sleep(1)

		self.write_log()
		self.update_rlv_files()


	def check_complete(self):

		try:
			# Expect the line of iteration data from Goma
			self.child.expect('\s[:0-9]+\s+[0-9\[\]]+\s+[.0-9+\-e]+\s+[.0-9+\-e]+\s+[.0-9+\-e]+\s+[.0-9+\-e]+\s+[.0-9+\-e]+\s+[.0-9+\-e]+\s+\d\s+[.0-9+\-e/]+')
			self.child.send('')
			

		except pexpect.EOF:	
			self.complete = True

			with open(self.pxlog_filename, 'rb') as f:
				lines = f.read()
				lines = lines.decode("utf-8") 

				if 'Failure:' in lines:
					self.completion_type = 'Failure'
				elif 'ERROR' in lines:
					self.completion_type = 'Error'
				else:
					self.completion_type = 'Success'

				print(self.completion_type)

	def write_log(self):
		log_list = list()
		log_list.append('Input file: ' + self.input_filename)
		log_list.append('Run line: ' + self.run_line)
		log_list.append('Completion type: ' + self.completion_type)

		with open(self.pxlog_filename, "r") as f2:
			pxlogread = f2.read()

		with open(self.fulllog_filename, "w") as f1:
			for line in log_list:
				f1.write(line + '\n')

			f1.write('\n')
			f1.write(pxlogread)

		os.remove(self.pxlog_filename) 
		self.rlv_files.add(self.fulllog_filename)


	def update_rlv_files(self):
		after_file_list = [file for file in os.listdir(self.run_path) if os.path.isfile(file)]
		# exclude_files = glob.glob('*_tgplog.txt') + glob.glob('tmp_*.d')
		# after_files_list = [file for file in after_file_list if file not in exclude_files]
		after_files_list = [file for file in after_file_list if os.path.getmtime(file) > self.run_time]

		self.rlv_files.update(after_files_list)

	def save_session(self):
		

		new_session_path = os.path.join(self.run_path, self.session_name)

		print('Creating directory ' + self.session_name)

		if os.path.exists(self.session_name):
			print('Session ' + self.session_name + ' already exists.  Files will be overwritten')
		else:
			os.mkdir(self.session_name)

		# Copy all the important stuff into the new folder
		# figure out where rlv file comes from
		for file in self.rlv_files:

			# Check if the file exists
			if os.path.exists(os.path.join(self.run_path,file)):

				# Rename temporary files (tgp = temporary goma pexpect)
				if '_tgplog.txt' in file:
					new_file_name = file.replace('_tgplog.txt', '_log.txt')
				elif '.xlsx' in file:
					new_file_name = file.replace('.xlsx', '_' + self.session_name + '_' + self.runID + '.xlsx')
				else:
					new_file_name = file

				new_dest = os.path.join(self.session_name, os.path.basename(os.path.normpath(new_file_name)))

				# Copy the file
				print('Copying ' + os.path.basename(file) + ' to ' + os.path.join(self.session_name, os.path.basename(new_file_name)))
				copy(file, new_dest)

				# Delete the temporary log
				if '_tgplog.txt' in file:
					os.remove(file)

			else:
				print('Expected file ' + file + ' is missing.  Skipping.')

	@staticmethod
	def send_pushover(the_message):
		pass
		# conn = httplib.HTTPSConnection("api.pushover.net:443")
		# pushover_user_key = 'uqjndbgb4jyawdw64x9vo28c2of2u9'
		# pushover_app_token = 'abq4cibvf2ang8s8unkx5ftyg2a5hr'
		# conn.request("POST", "/1/messages.json",
		#   urllib.urlencode({
		#     "token": pushover_app_token,
		#     "user": pushover_user_key,
		#     "message": the_message,
		#   }), { "Content-type": "application/x-www-form-urlencoded" })
		# conn.getresponse()


	# This method finds the value after an equal sign in the input file
	# Arguments: array of lines of input file (comments removed)
	# Returns: a string of the value after the equal sign w/o any spaces
	@staticmethod
	def line_finder(lines, substring):
		line = next((s for s in lines if substring in s), None)
		if line is not None:
			value = line.split('=')[-1].strip()
			return value
		else:
			return None

	# A mini parser for Goma.  Could be expanded to create an entire Gopyxl file if need be
	# Arguments: Input file filepath
	# Returns: Currently a dictionary of relevant FEM files
	@staticmethod
	def goma_mini_parser(input_filename):
		with open(input_filename) as f:
			lines = [s for s in f.readlines() if '#' not in s]

			# pdb.set_trace()

			FEM_file_dict = dict()
			FEM_file_dict['FEM file'] = Gorun.line_finder(lines, 'FEM file')
			FEM_file_dict['Output EXODUS II file'] = Gorun.line_finder(lines, 'Output EXODUS II file')
			FEM_file_dict['GUESS file'] = Gorun.line_finder(lines, 'GUESS file')
			FEM_file_dict['SOLN file'] = Gorun.line_finder(lines, 'SOLN file')
			FEM_file_dict['Output EXODUS II file'] = Gorun.line_finder(lines, 'Output EXODUS II file')
			FEM_file_dict['Write intermediate results'] = Gorun.line_finder(lines, 'Write intermediate results')

		return FEM_file_dict