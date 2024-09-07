# ANSI escape sequences for colors and formatting

BOLD = '1'
UNDERLINE = '4'
BLINK = '5'
INVERT = '7'
CONCEALD = '8'
STRIKE = '9'

###################

GREY = '30'
RED = '31'
GREEN = '32'
YELLOW = '33'
BLUE = '34'
MAGENTA = '35'
CYAN = '36'
WHITE = '37'
BLACK = '90'

BRED = '91'
BGREEN = '92'
BYELLOW = '93'
BBLUE = '94'
BMAGENTA = '95'
BCYAN = '96'
BWHITE = '97'

###################

BG_BLACK = '40'
BG_RED = '41'
BG_GREEN = '42'
BG_YELLOW = '43'
BG_BLUE = '44'
BG_MAGENTA = '45'
BG_CYAN = '46'
BG_WHITE = '47'

BG_BBLACK = '100'
BG_BRED = '101'
BG_BGREEN = '102'
BG_BYELLOW = '103'
BG_BBLUE = '104'
BG_BMAGENTA = '105'
BG_BCYAN = '106'
BG_BWHITE = '107'

###################

ENDC = '\033[0m'

# Functions

def pformat(str, *args):
	if args:
		ANSI = '\033['
		for arg in args:
			ANSI += arg + ';'
		ANSI = ANSI[:-1] + 'm'

		return ANSI + str + ENDC
	else:
		return str
	
def pprint(str, *args, **kwargs):
	end = kwargs.get('end', '\n')

	print(pformat(str, *args), end=end)

def pinput(str, *args):
	return input(pformat(str, *args))

def mpprint(*segments):
	for segment in segments:
		if segment.__class__ == list:
			string = str(segment[0])
			pprint(string, *segment[1:], end='')
		else:
			print(segment, end='')
	print()