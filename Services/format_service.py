color = {
   'purple': '\033[95m',
   'cyan': '\033[96m',
   'darkcyan': '\033[36m',
   'blue': '\033[94m',
   'green': '\033[92m',
   'yellow': '\033[93m',
   'red': '\033[91m',
   'bold': '\033[1m',
   'underline': '\033[4m',
   'end': '\033[0m',
}


def pretty_print(text, format):
    if str(format) in color:
        print(color[format] + str(text) + color['end'])