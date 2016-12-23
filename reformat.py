import csv
import sys

def main():
	fName = sys.argv[1]
	csvfile = open(fName,'rb')
	data = [i for i in csvfile]

	new_data = []
	for i in data:
		line = i.split(',')
		name = line[1]
		email = line[0]
		try:
			email = line[0][email.find('<')+1:email.find('>')]
		except:
			pass # for header values
		new_data.append([email, name])

	with open('new_'+fName,'wb') as f:
		writer = csv.writer(f)
		for i in new_data:
			writer.writerow([i[0], i[1]])

if __name__ == '__main__':
	main()