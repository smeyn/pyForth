"""Usage:
  Forth [<vocabulary> -l Logfile]

run the forth interpreter.

Options:
  <vocabulary>   path to vocabulary file [default: voc.json]
  -h --help
  -l LogFile

"""

from docopt import docopt
from Runtime import Interpreter
from os import path
from os import listdir

if __name__ == '__main__':

	s = listdir(".")
	arguments = docopt(__doc__)
	voc = arguments['<vocabulary>']
	if not voc:
		voc = 'voc.json'

	interpreter = Interpreter()
	interpreter.run()
