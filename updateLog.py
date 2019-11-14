import datetime, subprocess

print("Please enter your name:")
print("Format: firstnameL")
name = input()

print("\n")
print("Please enter your update:")
update = input()

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

devlogFile = open("./doc/devlog.txt", "a")

devlogFile.write("\n" + name + " -- " + timestamp + "\n")
devlogFile.write(update+"\n")

devlogFile.close()

subprocess.run(['git', 'add', '.'])
subprocess.run(['git', 'commit', '-m', name + ': ' + update])
subprocess.run(['git', 'push'])
