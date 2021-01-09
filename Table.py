import re


class Table:
    name = ''
    headers = []
    types = []
    data = []  # put a row list at each item

    def __init__(self, file=None, headers=False):
        csv = ''
        if file is not None:
            if file[-4:] == '.csv':
                self.name = file[:-4]
                csv = open(file)
                if (headers):
                    self.parseHeaders(csv.readline())
                    self.parseTable(csv)
                    self.checkTypes()

    def __del__(self):
        pass

    def parseTable(self, csv):
        with csv as data:  # while there are still lines to grab
            for raw_row in data:
                row = raw_row.replace(' ', '').replace(
                    '?', 'na').strip('\n').split(',')
            self.data.append(row)

    def parseHeaders(self, head_line):
        self.headers = head_line.replace(' ', '').split(',')
        for i in range(self.headers):
            self.headers[i] = self.headers[i].replace(' ', '_')
            if self.headers[i] == '':
                self.headers[i] = 'index'

    def checkTypes(self):
        self.types = [None] * len(self.headers)
        for row_y in self.data:
            for x in range(row_y):
                if re.match(r'(?i)n\/?a', row_y[x]):
                    continue
                elif re.match(r'^\d+$', row_y[x]):
                    self.types[x] = 'INTEGER'
                elif re.match(r'[+-]?([0-9]*[.])?[0-9]+', row_y[x]):
                    self.types[x] = 'FLOAT'

    def getRow(self, rowNum):
        return self.data[rowNum]

    def getCol(self, colNum):
        if isinstance(colNum, str):
            colNum = self.headers.index(colNum)
        ret = []
        for i in range(len(self.data)):
            ret.append(self.data[i][colNum])
        return ret
# above is 100%
# below is sql exporting

    def buildTableData(self, f, out):
        for r in self.data:
            out.write('INSERT INTO ' + f + ' (' + str(self.types).strip(
                r'\[\]\n') + ') VALUES (' + str(r).strip(r'\[\]').replace("'", "") + ');\n')

    def exportSql(self):
        f_name = re.search(r'[ \w-]+?(?=\.)', self.name).group(0)
        sql = open(f_name, 'w+')
        sql.write('DROP TABLE IF EXISTS ' + f_name +
                  ';\nCREATE TABLE ' + f_name + ' (\n')
        for i in range(len(self.headers)):
            self.headers[i] = self.headers[i].replace(' ', '_').strip('\"\n')
            line_comma = ',' if len(self.headers)-1 != i else ''
            if self.headers[i] == "":
                self.headers[i] = 'index'
            if self.headers[i].find('id') >= 0 or self.headers[i].find('num') >= 0:
                t = ' BIGINT UNSIGNED'
                t += ',' if self.headers[i] != 'id' else ' NOT NULL AUTO_INCREMENT PRIMARY KEY' + line_comma
            elif self.types[i] != None:
                t = ' ' + self.types[i] + line_comma
            elif self.headers[i].find('date') >= 0:
                t = ' TIMESTAMP NOT NULL' + line_comma
            else:
                t = ' VARCHAR(255)' + line_comma
            sql.write('\t' + self.headers[i].replace(' ', '_') + t + '\n')
        sql.write(');\n\n')
        self.buildTableData(f_name, sql)
