import sys
import re
import os


def writeTableData(data, out):
    for r in data.split('\n'):
        out.write(r + '\n')
        r = data.split('\n')


def buildTableData(csv, f, attrs, out):
    r = csv.readline()
    data = ''
    types = [None] * len(attrs)
    while True:
        if r == '':
            break
        values = []
        i = 0
        for col in r.split(','):
            val = col.replace(' ', '_').strip('\"\n')
            if re.match(r'^\d+$', val):
                types[i] = 'INTEGER'
            elif re.match(r'[+-]?([0-9]*[.])?[0-9]+', val):
                types[i] = 'FLOAT'
            values.append(val)
            i += 1
        data += 'INSERT INTO ' + f + ' (' + str(attrs).replace("'", "").strip(
            r'\[\]\n') + ') VALUES (' + str(values).strip(r'\[\]').replace("'", "") + ');\n'
        r = csv.readline()

    return data, types


def buildTable(f, out):
    f_name = re.search(r'[ \w-]+?(?=\.)', f).group(0)
    out.write('DROP TABLE IF EXISTS ' + f_name + ';\n')
    out.write('CREATE TABLE ' + f_name + ' (\n')
    csv = open(f, 'r')
    raw_headers = csv.readline().split(',')
    data, pred_types = buildTableData(csv, f_name, raw_headers, out)
    for i in range(len(raw_headers)):
        raw_headers[i] = raw_headers[i].replace(' ', '_').strip('\"\n')
        line_comma = ',' if len(raw_headers)-1 != i else ''
        if raw_headers[i] == "":
            raw_headers[i] = 'index'
        if raw_headers[i].find('id') >= 0 or raw_headers[i].find('num') >= 0:
            t = ' BIGINT UNSIGNED'
            t += ',' if raw_headers[i] != 'id' else ' NOT NULL AUTO_INCREMENT PRIMARY KEY' + line_comma
        elif pred_types[i] != None:
            t = ' ' + pred_types[i] + line_comma
        elif raw_headers[i].find('date') >= 0:
            t = ' TIMESTAMP NOT NULL' + line_comma
        else:
            t = ' VARCHAR(255)' + line_comma
        out.write('\t' + raw_headers[i].replace(' ', '_') + t + '\n')
    out.write(');\n\n')
    writeTableData(data, out)


def getFileName(unreadable):
    return input('Enter a better filename for ' + unreadable + ' the schema file: ')


def readDir(path, out):
    for dirpath, subdirs, files in os.walk(path):
        for dir in subdirs:
            readDir(dirpath + dir, out)
        for f in files:
            if f[-4:] == '.csv':
                buildTable(path + f, out)


def createSchema(dir):
    out = ''
    if dir == './':
        file_name = getFileName(dir)
        out = open('./' + file_name + '.sql', 'w+')
        out.write('DROP SCHEMA IF EXISTS ' + file_name + ';\n')
        out.write('CREATE SCHEMA ' + file_name + ';\n\n')
        out.write('USE ' + file_name + ';\n\n')
    else:
        out = open('./' + dir + '.sql', 'w+')
        out.write('DROP SCHEMA IF EXISTS ' + dir + ';\n')
        out.write('CREATE SCHEMA ' + dir + ';\n\n')
        out.write('USE ' + dir + ';\n\n')
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('ERR format: python3 csvToSql.py <path/to/csv>')
        exit(1)

    if os.path.isfile(sys.argv[1]):
        buildTable(sys.argv[1], getFileName(sys.argv[1]))
    elif os.path.isdir(sys.argv[1]):
        outfile = createSchema(sys.argv[1])
        readDir(sys.argv[1], outfile)
