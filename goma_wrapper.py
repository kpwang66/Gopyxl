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
from Gorun_v2 import *


def flagstr2dict(flags_dict, flag_string):
	flags_w_str_arg = ['-brk', '-rest', 'i', 'input', '-ix', '-inexoII', '-ox', '-outexoII', '-s', '-soln', '-se', '-stderr', '-so', '-stdout']
	flags_w_flt_arg = ['-ts', '-te', '-cb', '-ce', '-cd', '-cmin', '-cmax', '-r']
	flags_w_int_arg = ['-d', '-debug', '-n', '-newton', '-cn', '-cm', '-ct', '-c_bc', '-c_df', '-c_mn', '-c_mp', '-time_pl']
	flags_w_non_arg = ['-h', '-help', '-nd', '-nodisplay', '-bc_list', '-wr_int']
	strsplit = flag_string.strip().split(' ')

	i = 0
	while i < len(strsplit):

		# Sort which flags expect which types of arguments

		if strsplit[i] in flags_w_str_arg:
			flags_dict[strsplit[i]] = strsplit[i+1] # add this entry 
			i = i+2
		elif strsplit[i] in flags_w_flt_arg: 
			flags_dict[strsplit[i]] = float(strsplit[i+1]) # add this entry 
			i = i+2
		elif strsplit[i] in flags_w_int_arg: 	
			flags_dict[strsplit[i]] = int(strsplit[i+1]) # add this entry 
			i = i+2
			print('expected int and that\'s what i got')
		elif strsplit[i] in flags_w_non_arg:
			flags_dict[strsplit[i]] = ''
			i = i+1 # add this entry 
		else:
			print(flag_string + ' is not a recognized Goma flag.')
			i = i+1


	# pdb.set_trace()

	return flags_dict

def flags_dict_preview(flags_dict):
	return ' '.join([key + ' ' +str(flags_dict[key]) for key in flags_dict])
	

def clear_tmp_files():
	tgps_logs = glob.glob('*_tgplog.txt')
	tmpd_files = glob.glob('tmp_*.d')
	print('Clearing temp files:')
	for tmp_file in tgps_logs + tmpd_files:
		print('\tDeleting ' + tmp_file)
		os.remove(tmp_file)


def get_new_session_name():
	today_mdy = datetime.datetime.today().strftime('%m-%d-%Y')

	session_dirs = get_session_names()
	session_dates = [name.split('_')[0] for name in session_dirs]

	if today_mdy in session_dates:
		todays_sessions = [int(name.split('_')[1].split('-')[1]) for name in glob.glob(today_mdy + '_sn-' + '[0-9]'*3)]
		latest_session = max(todays_sessions)
		new_session_name = today_mdy + '_sn-' + str(latest_session + 1).zfill(3)
	else:
		new_session_name = today_mdy + '_sn-001'

	return new_session_name

def get_session_names():
	session_dirs = glob.glob('[0-1][0-9]-[0-3][0-9]-' + '[0-9]'*4 + '_sn-' + '[0-9]'*3)

	return session_dirs


#### Main stuff starts here ###	
path = os.getcwd()

# First check if there are any input files
input_list = [f for f in os.listdir(path) if f.endswith('.inp')]
input_list = [input for input in input_list if 'echo_' not in input]

# If input.inp exists, place it at the front of the list because it's the default
if 'input.inp' in input_list:
	input_list.insert(0, input_list.pop(input_list.index('input.inp')))

# print sys.argv 
input_filename = 'input.inp' #hardcode this for now


# Check if there is a custom input file name.  Otherwise, check for any *.inp file.  Otherwise, the input filename
# the wrapper looks for is input.inp by default.
if len(sys.argv) == 2:
	input_filename = sys.argv[1]
elif len(input_list) == 0:
	print ('No input files (*.inp) detected.  Wrapper closing.')
	sys.exit()
elif len(input_list) > 1:
	print ('\n Multiple *.inp files detected.  Which input file to load?')
	for index, input_file_option in enumerate(input_list):
		print(" " + str(index+1) + " " + input_file_option)
	input_i = input("\nInput file choice: ")
	input_filename = input_list[int(input_i)-1]

print('Input file selected: ' + input_filename)



# pdb.set_trace()

# Path to run Goma.  Edit this as necessary.
goma_path = '/home/kerry/spack/opt/spack/linux-ubuntu20.04-x86_64_v4/gcc-9.4.0/goma-7.1.1-4pmbhwpvn63imkdbalyyxf5u2h4zk2r4/bin/goma'


print("\n\nGoma Wrapper \n\n")

gopyxl_list = [f for f in os.listdir(path) if f.endswith('.gopyxl')]

try: # to read from a Gopyxl file if available
	gopyxl_filename = gopyxl_list[0]
	gopyxl_filename = path + '/' + gopyxl_filename
	gopyxl_read = True
except:
	Exception('No gopyxl file detected in ' + path)
	gopyxl_read = False
	gopyxl_filename = None


session_dirs = get_session_names()
new_session_name = get_new_session_name()

print("\nSession name: " + new_session_name)
wrapper_options = ['Run Goma', 'Add flags', 'Load Guess/Cont solution', 'Run with auto-Newton Factor', \
					'Debug mode', 'Save session', 'Exit without saving session', 'Exit and save session']

time.sleep(1)

goma_run_yet = False
Gorun_list = list()
# flag_list = list()
flags_dict = dict()

copy(Gorun.goma_mini_parser(input_filename)['FEM file'], 'guess.exoII')
print(Gorun.goma_mini_parser(input_filename)['FEM file'] + ' --> guess.exoII')
while True:
	print('Run line: ' + 'goma -i ' + input_filename + ' ' + flags_dict_preview(flags_dict))
	print("")
	if goma_run_yet == False:
		print ('Goma has NOT run yet')
	else:
		print ('Goma has ALREADY run')


	for index, option in enumerate(wrapper_options):
		print(" " + str(index+1) + " " + option)

	
	usr_response = input("\nGoma Wrapper Choice: ")

	try:
		selected_option = wrapper_options[int(usr_response) - 1]
	except:
		selected_option =''

	print('You selected ' + str(usr_response) + " " + selected_option)

	if selected_option == 'Run Goma':

		# launch_goma()
		# before_file_list = [file for file in os.listdir('.') if os.path.isfile(file)]

		Gorun_time = time.time()
		this_run = Gorun(new_session_name, goma_path = goma_path, run_path = path, input_filename=input_filename, gopyxl_filename=gopyxl_filename, flags_dict=flags_dict)
		Gorun_list.append(this_run)
		goma_run_yet = True

		after_file_list = [file for file in os.listdir('.') if os.path.isfile(file)]

		exclude_files = glob.glob('*_tgplog.txt') + glob.glob('tmp_*.d')
		after_files_list = [file for file in after_file_list if file not in exclude_files]
		after_files_list = [file for file in after_file_list if os.path.getmtime(file) > Gorun_time]

		# pdb.set_trace()

	elif selected_option =='Add flags':
		temp_run = pexpect.spawn(goma_path + ' -help', timeout=1.5, maxread=4000)
		temp_run.interact()
		goma_flags = input("\nEnter flags and run: ")
		flags_dict = flagstr2dict(flags_dict, goma_flags)


		# this_run = Gorun(new_session_name, input_filename = input_filename, flags_dict= flags_dict)
		# goma_run_yet = True
		# Gorun.list.append(this_run)

	elif selected_option =='Load Guess/Cont solution':
		session_dirs = get_session_names()
		session_dirs.sort(reverse=True)
		session_dirs.insert(0, 'Load last saved session')
		session_dirs.insert(1, 'Load last out.exoII')
		for index, session_name in enumerate(session_dirs):
			print(" " + str(index+1) + " " + session_name)

		selected_session_input = input("\nLoad session choice: ")
		# pdb.set_trace()

		if selected_session_input == 'q':
			continue
		elif int(selected_session_input) == 1:
			print(os.path.join(session_dirs[2], 'out.exoII') + ' --> guess.exoII')
			copy(os.path.join(session_dirs[2], 'out.exoII'), 'guess.exoII')
			
			# pdb.set_trace()
			# selected_session = session_dirs[1]
		elif int(selected_session_input) == 2:
			# pdb.set_trace()
			copy('out.exoII', 'guess.exoII')
			print('out.exoII --> guess.exoII')
		elif int(selected_session_input) > 1:
			try:
				selected_session = session_dirs[int(selected_session_input) - 1]
				print(os.path.join(selected_session, 'out.exoII') + ' --> guess.exoII')
				copy(os.path.join(selected_session, 'out.exoII'), 'guess.exoII')
				
			except IndexError:
				error('Invalid choice')
				continue

	
		# flags_dict['-ix'] = selected_session + '_outsl.exoII'

		# guess_exoII_path = os.path.join(path, selected_session, 'out.exoII')
		# print(selected_session+'/out.exoII --> ./guess.exoII')
		# copy(guess_exoII_path, os.path.join(path,'guess.exoII'))

		
	elif selected_option =='Run with auto-Newton Factor':
		pass
	# 	current_NF = 1
	# 	goma_run_attempt_count = 1

	# 	while True: 

	# 		flags_dict = {'-r':str(current_NF)}
	# 		this_run = Gorun(new_session_name, input_filename = input_filename, wait = False, interact=False, flags = flags_dict)
	# 		# goma = launch_goma(wait = False, interact=False)
	# 		goma_run_yet = True

	# 		print('  ToD    itn   L_oo    L_1     L_2     L_oo    L_1     L_2   lis  asm/slv (sec)')
	# 		print('-------- --- ------- ------- ------- ------- ------- ------- --- ---------------')
	# 		this_run.child.expect('-------- --- ------- ------- ------- ------- ------- ------- --- ---------------')
	# 		this_run.child.sendline('')
	# 		iter_log = list()
	# 		newton_i_count = 1
	# 		current_r_Loo = 1e10
	# 		while True: # inner loop checks the iteration/norm progress
	# 			time.sleep(1)  # Check every this number of seconds
	# 			try:
	# 				# Expect the line of iteration data from Goma
	# 				this_run.child.expect('\s[:0-9]+\s+[0-9\[\]]+\s+[.0-9+\-e]+\s+[.0-9+\-e]+\s+[.0-9+\-e]+\s+[.0-9+\-e]+\s+[.0-9+\-e]+\s+[.0-9+\-e]+\s+\d\s+[.0-9+\-e/]+')
	# 				this_run.child.sendline('')
	# 				goma_iter_line = this_run.child.after.replace('\r', '').replace('\n', '')
	# 				iter_log.append(goma_iter_line)
	# 				print(goma_iter_line)
	# 				prev_r_Loo = current_r_Loo
	# 				current_r_Loo = float(goma_iter_line.split()[2])

	# 				if current_r_Loo > prev_r_Loo: # Check if current norm is larger than the previous norm

	# 					# Decrease current_NF
	# 					print ('Prev norm was ' + str(prev_r_Loo) + '.  Current norm is ' + str(current_r_Loo) + '. \n')
	# 					current_NF = current_NF*0.8
	# 					print('Norm is increasing.  Decreasing Newton factor to ' + str(current_NF) + '. Terminating current session.')
	# 					this_run.child.terminate()
	# 					goma_natural_terminated = False

	# 					time.sleep(1)

	# 					break
						
	# 					# Find last saved session and set that as the name to run w the next time

	# 			# Check to see if you've found the solution!

	# 			except pexpect.EOF:	
	# 				goma_natural_terminated = True
	# 				break

	# 			newton_i_count = newton_i_count+1
			
	# 		if goma_natural_terminated:
	# 			print('Goma either finished or crashed!')

	# 			# with open(logfile_name, 'rb') as f:
	# 			# 	lines = [s for s in f.readlines() if '#' not in s]
	# 			# 	# if 
	# 			break

	# 		goma_run_yet = True

	# 		if goma_run_attempt_count >= 3:
	# 			print('Newton factor has been decreased 3 times already.  Recommend a different approach.')
	# 			break
	# 		else:
	# 			goma_run_attempt_count = goma_run_attempt_count + 1

	# 		# pdb.set_trace()
		
	elif selected_option =='Debug mode':
		print('this_run = current Gorun object')
		pdb.set_trace()

	elif selected_option =='Save session(s)':	

		if len(Gorun_list) > 0:
			print ('Did we make it in?')
			for Gorun in Gorun_list:
				Gorun.save_session(path)
				print('Copying a bunch of files')
			else:
				print('Goma not run!')

	elif selected_option =='Exit without saving session':
		if goma_run_yet == True:
			usr_response = input("\nGoma has run.  Exit without saving session? (y/n): ")
			if usr_response == 'y':
				clear_tmp_files()
				break
			else:
				continue
		else:
			clear_tmp_files()
			break
	elif selected_option =='Exit and save session':
		if len(Gorun_list) > 0:
			for Gorun in Gorun_list:
				Gorun.save_session()
				print('Copying a bunch of files')
			clear_tmp_files()
			break
		else:
			print('Goma not run!')

	else:
		continue
		
	
print ("All done!")