
IS_COMMAND = b'\xf0'
COLOR = 240
COLOR_OFF = 241
PRIORITY = 242
PRIORITY_OFF = 243
Y_CORNER = 244
X_CORNER = 245
LINE = 246
SHORT_LINE = 247
FILL = 248
PEN = 249
PLOT = 250
END = 255

COMMAND_DEFS = {240: COLOR,
		241: COLOR_OFF,
		242: PRIORITY,
                243: PRIORITY_OFF,
                244: Y_CORNER,
                245: X_CORNER,
                246: LINE,
                247: SHORT_LINE,
                248: FILL,
                249: PEN,
                250: PLOT,
                255: END}

COMMAND_LABELS = {240: 'COLOR',
	       	241: 'COLOR_OFF',
		242: 'PRIORITY',
                243: 'PRIORITY_OFF',
                244: 'Y_CORNER',
                245: 'X_CORNER',
                246: 'LINE',
                247: 'SHORT_LINE',
                248: 'FILL',
                249: 'PEN',
                250: 'PLOT',
                255: 'END'}


    


