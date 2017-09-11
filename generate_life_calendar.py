import datetime
import argparse
import sys
import os
import cairo

DOC_WIDTH = 1872   # 26 inches
DOC_HEIGHT = 2880  # 40 inches
DOC_NAME = "life_calendar.pdf"
DOC_TITLE = "LIFE CALENDAR"

KEY_NEWYEAR_DESC = "First week of the new year"
KEY_BIRTHDAY_DESC = "Week of your birthday"

FONT = "Brocha"
BIGFONT_SIZE = 48
SMALLFONT_SIZE = 16
TINYFONT_SIZE = 12

NUM_ROWS = 90
NUM_COLUMNS = 52

Y_MARGIN = 144
BOX_MARGIN = 10

BOX_SIZE = ((DOC_HEIGHT - (Y_MARGIN + 36)) / NUM_ROWS) - BOX_MARGIN
X_MARGIN = (DOC_WIDTH - ((BOX_SIZE + BOX_MARGIN) * NUM_COLUMNS)) / 2

BIRTHDAY_COLOUR = (0.5, 0.5, 0.5)
NEWYEAR_COLOUR = (0.8, 0.8, 0.8)

parser = argparse.ArgumentParser(description='\nGenerate a personalized "Life '
    ' Calendar", inspired by the calendar with the same name from the '
    'waitbutwhy.com store')

parser.add_argument(type=str, dest='date', help='your birthday, in either '
    'dd/mm/yyyy or dd-mm-yyyy format')

parser.add_argument('-f', '--filename', type=str, dest='filename',
    help='output filename', default=DOC_NAME)

args = parser.parse_args()

def parse_date(date):
    formats = ['%d/%m/%Y', '%d-%m-%Y']
    stripped = date.strip()

    for f in formats:
        try:
            ret = datetime.datetime.strptime(date, f)
        except:
            continue
        else:
            return ret

    return None

START_DATE = parse_date(args.date)
if START_DATE == None:
    print "Error: incorrect date format\n"
    parser.print_help()
    sys.exit(1)

doc_name = '%s.pdf' % (os.path.splitext(args.filename)[0])
surface = cairo.PDFSurface (doc_name, DOC_WIDTH, DOC_HEIGHT)
ctx = cairo.Context(surface)

def draw_square(pos_x, pos_y, fillcolour=(1, 1, 1)):
    """
    Draws a square at pos_x,pos_y
    """

    ctx.set_line_width(4)
    ctx.set_source_rgb(0, 0, 0)
    ctx.move_to(pos_x, pos_y)

    ctx.rectangle(pos_x, pos_y, BOX_SIZE, BOX_SIZE)
    ctx.stroke_preserve()

    ctx.set_source_rgb(*fillcolour)
    ctx.fill()

def text_size(text):
    _, _, width, height, _, _ = ctx.text_extents(text)
    return width, height

def is_current_week(now, month, day):
    end = now + datetime.timedelta(weeks=1)
    date1 = datetime.datetime(now.year, month, day)
    date2 = datetime.datetime(now.year + 1, month, day)

    return (now <= date1 < end) or (now <= date2 < end)

def draw_row(pos_y, date):
    """
    Draws a row of 52 squares, starting at pos_y
    """

    pos_x = X_MARGIN

    for i in range(NUM_COLUMNS):
        fill=(1, 1, 1)

        if is_current_week(date, START_DATE.month, START_DATE.day):
            fill = BIRTHDAY_COLOUR
        elif is_current_week(date, 1, 1):
            fill = NEWYEAR_COLOUR

        draw_square(pos_x, pos_y, fillcolour=fill)
        pos_x += BOX_SIZE + BOX_MARGIN
        date += datetime.timedelta(weeks=1)

def draw_key_item(pos_x, pos_y, desc, colour):
    draw_square(pos_x, pos_y, fillcolour=colour)
    pos_x += BOX_SIZE * 2

    ctx.set_source_rgb(0, 0, 0)
    w, h = text_size(desc)
    ctx.move_to(pos_x, pos_y + (BOX_SIZE / 2) + (h / 2))
    ctx.show_text(desc)

    return pos_x + w + (BOX_SIZE * 2)

def draw_grid(date):
    """
    Draws the whole grid of 52x90 squares
    """
    pos_y = BOX_SIZE
    pos_x = X_MARGIN / 2

    # Draw the key for box colours
    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_NORMAL)

    pos_x = draw_key_item(pos_x, pos_y, KEY_BIRTHDAY_DESC, BIRTHDAY_COLOUR)
    draw_key_item(pos_x, pos_y, KEY_NEWYEAR_DESC, NEWYEAR_COLOUR)

    # draw week numbers above top row
    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_NORMAL)

    pos_x = X_MARGIN
    pos_y = Y_MARGIN
    for i in range(NUM_COLUMNS):
        ctx.move_to(pos_x, pos_y - BOX_SIZE)
        ctx.show_text(str(i + 1))
        pos_x += BOX_SIZE + BOX_MARGIN

    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_ITALIC,
        cairo.FONT_WEIGHT_NORMAL)

    for i in range(NUM_ROWS):
        # Generate string for current date
        ctx.set_source_rgb(0, 0, 0)
        date_str = date.strftime('%d %b, %Y')
        w, h = text_size(date_str)

        # Draw it in front of the current row
        ctx.move_to(X_MARGIN - w - BOX_SIZE,
            pos_y + ((BOX_SIZE / 2) + (h / 2)))
        ctx.show_text(date_str)

        # Draw the current row
        draw_row(pos_y, date)

        # Increment y position and current date by 1 row/year
        pos_y += BOX_SIZE + BOX_MARGIN
        date += datetime.timedelta(weeks=52)

def main():
    # Fill background with white
    ctx.set_source_rgb(1, 1, 1)
    ctx.rectangle(0, 0, DOC_WIDTH, DOC_HEIGHT)
    ctx.fill()

    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD)
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_font_size(BIGFONT_SIZE)
    w, h = text_size(DOC_TITLE)
    ctx.move_to((DOC_WIDTH / 2) - (w / 2), (Y_MARGIN / 2) - (h / 2))
    ctx.show_text(DOC_TITLE)

    # Draw 52x90 grid of squares
    draw_grid(START_DATE)
    ctx.show_page()
    print 'Created %s' % doc_name

if __name__ == "__main__":
    main()
