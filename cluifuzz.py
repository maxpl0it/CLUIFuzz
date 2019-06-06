import subprocess, random, time, os, shutil, signal, argparse
from multiprocessing import Process, Value


def execute_char(test_folder, value, pid, binary):
	p = subprocess.Popen([binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
	pid.value = p.pid
	while True:
		try:
			char = chr(random.randint(0, 255))
			with open("exploit_{}".format(test_folder), 'ab') as f:
				f.write(char)
			p.stdin.write(char)
		except:
			break
	while p.poll() is None:
		time.sleep(0.001)
	if p.returncode < 0:
		print("[+] Identified potential crashing input")
		os.system("screen -d -m sh -c 'cat exploit_{} | {}; echo $? > verify_exploit_result'".format(test_folder, binary))
		time.sleep(0.5)
		with open("verify_exploit_result", 'r') as f:
			result = int(f.read())
			if result in [0, 1]:
				print("[-] Could not verify")
				value.value = 0
			else:
				print("[+] Verifed!")
				value.value = 1
	else:
		print("[-] Test did not result in a crash.")
		value.value = 0


def execute_exploit(exploit, value, pid, binary):
	with open("verify_exploit", 'wb') as f:
		f.write(exploit)
	os.system("screen -d -m sh -c 'cat verify_exploit | {}; echo $? > verify_exploit_result'".format(binary))
	time.sleep(0.5)
	with open("verify_exploit_result", 'r') as f:
		result = int(f.read())
	if result in [0, 1]:
		print("[-] Could not verify")
		value.value = 0
	else:
		print("[+] Verifed!")
		value.value = 1


def execute_test(binary, test_folder, exploit=None):
	value = Value('i', -1)
	pid = Value('i', 0)
	multip = Process(target=execute_char if exploit is None else execute_exploit, args=(test_folder if exploit is None else exploit, value, pid, binary))
	multip.start()
	multip.join(5)
	if multip.is_alive():
		print("[-] Test timed out")
		try:
			if exploit is None:
				os.killpg(os.getpgid(pid.value), signal.SIGTERM)
		except:
			pass
		multip.terminate()
		time.sleep(0.1)
		return False
	if value.value == 1:
		try:
			if exploit is None:
				os.killpg(os.getpgid(pid.value), signal.SIGTERM)
		except:
			pass
		return True
	try:
		if exploit is None:
			os.killpg(os.getpgid(pid.value), signal.SIGTERM)
	except:
		pass
	return False


def reducer(binary, test_folder):
	exploit = ""
	with open("exploit_{}".format(test_folder), 'rb') as f:
		exploit = f.read()
	current_test = ""
	print("[!] Verifying")
	print("[!] Success: {}".format(execute_test(binary, test_folder, exploit=exploit)))
	for i in range(len(exploit)):
		test = current_test + exploit[i + 1:]
		result = execute_test(binary, test_folder, exploit=test)
		if not result:
			print("[+] Keeping char {}".format(i))
			current_test += exploit[i]
		else:
			print("[-] Ditching char {}".format(i))
	with open("exploit_{}_reduced".format(test_folder), 'wb') as f:
		f.write(current_test)
	print("[+] Reduced PoC from {} bytes to {} bytes".format(len(exploit), len(current_test)))
	print("[+] New PoC: test_{}/exploit_{}_reduced".format(test_folder, test_folder))


if __name__ == "__main__":
	print("   ________    __  ____________             \n  / ____/ /   / / / /  _/ ____/_  __________\n / /   / /   / / / // // /_  / / / /_  /_  /\n/ /___/ /___/ /_/ // // __/ / /_/ / / /_/ /_\n\\____/_____/\\____/___/_/    \\__,_/ /___/___/\n            Command-Line UI Fuzzer\n")

	parser = argparse.ArgumentParser(description='Command-line UI Fuzzer - Throws random characters (and control characters) at a given program until a timeout or a crash')
	parser.add_argument('binary_location', type=str, help='The mode to operate in')
	parser.add_argument('test_name', type=str, help='The mode to operate in')
	parser.add_argument('mode', choices=['fuzz', 'reduce'], default='fuzz', help='The mode to operate in')
	args = parser.parse_args()

	binary = args.binary_location
	test_folder = args.test_name
	mode = args.mode

	if mode == "reduce":
		try:
			os.chdir("test_{}".format(test_folder))
			reducer(binary, test_folder)
			print("[-] Reduction complete!")
		except:
			print("[-] No crash case in test_{}".format(test_folder))
		exit()

	while True:
		try:
			os.mkdir("test_{}".format(test_folder))
		except:
			print("[-] test_{} already exists. Delete it or reduce it.".format(test_folder))
			exit()
		os.chdir("test_{}".format(test_folder))
		with open("exploit_{}".format(test_folder), 'w') as f:
			f.write("")
		if execute_test(binary, test_folder):
			print("[+] Success! PoC at /test_{}/exploit_{}".format(test_folder, test_folder))
			exit()
		os.chdir("..")
		shutil.rmtree("test_{}".format(test_folder))
