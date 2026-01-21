import calendar
import argparse
from datetime import datetime, timezone, timedelta
from lunardate import LunarDate
from skyfield.api import load
from PIL import Image, ImageDraw, ImageFont

# ============================================================================
# CONSTANTS & GLOBAL SETUP
# ============================================================================
# Skyfield ephemeris data
ts = load.timescale()
eph = load('de421.bsp')
earth = eph['earth']
moon = eph['moon']
sun = eph['sun']

# Image dimensions: A4 300dpi landscape (3508x2480px)
WIDTH = 3508
HEIGHT = 2480
PADDING = 100

# Layout spacing
PSTART = 400
HSPACE = 680
WSPACE = 791
ASPACE = WSPACE // 7
WGAP = PADDING // 2
DGAP_OFFSET = 20
BGAP = 80

# Font sizes
FZ_YEAR = 300
FZ_MONTH = 80
FZ_WEEK = 40
FONT_NAME = "consolas.ttf"

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = 'red'
COLOR_BLUE = 'blue'
COLOR_GRAY_LIGHT = '#eeeeee'
COLOR_GRAY_BORDER = (180, 180, 180)
COLOR_YELLOW = (255, 255, 0)
COLOR_LUNAR_NEW_MOON = (255, 205, 210)
COLOR_LUNAR_FULL_MOON = (187, 222, 251)

# Weekday abbreviations
WEEKDAY_LIST = ['S', 'M', 'T', 'W', 'T', 'F', 'S']

# ============================================================================
# FUNCTIONS
# ============================================================================
def get_illum_waxing(date: datetime, draw_context: dict) -> tuple[float, bool]:
  """Get moon illumination and whether it's waxing."""
  t = draw_context['ts'].from_datetime(date)
  tn = draw_context['ts'].from_datetime(date + timedelta(days=1))

  illum = draw_context['earth'].at(t).observe(draw_context['moon']).apparent().fraction_illuminated(draw_context['sun'])
  illum_next = draw_context['earth'].at(tn).observe(draw_context['moon']).apparent().fraction_illuminated(draw_context['sun'])

  return illum, illum_next > illum


def get_lunar_color(date: datetime) -> int | None:
  """Get moon ring fill color based on lunar date."""
  lunar = LunarDate.fromSolarDate(date.year, date.month, date.day)

  if lunar.day == 1:
    return COLOR_LUNAR_NEW_MOON
  elif lunar.day == 15:
    return COLOR_LUNAR_FULL_MOON
  return None


def draw_moon_ring(cx: int, cy: int, radius: int, date: datetime, draw_context: dict) -> None:
  """Draw moon illumination ring at given position."""
  illum, waxing = get_illum_waxing(date, draw_context)

  bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
  start = -90
  sweep = int(360 * illum)

  if waxing:
    end = start + sweep
  else:
    end = start - sweep

  ellipse_color = get_lunar_color(date)

  draw_context['draw'].ellipse(bbox, fill=ellipse_color, outline=COLOR_GRAY_BORDER, width=2)
  draw_context['draw'].arc(bbox, start=0, end=360, fill=COLOR_YELLOW, width=4)
  draw_context['draw'].arc(bbox, start=start, end=end, fill=COLOR_BLACK, width=4)


def generate_calendar(tz_offset: int = 0, year: int = None) -> None:
  """Generate a calendar with moon phases for the specified year and timezone.
  
  Args:
    tz_offset: Timezone offset in hours (default: 0 for UTC)
    year: Year to generate calendar for (default: current year)
  """
  if year is None:
    year = datetime.now().year
  
  # Setup timezone and image
  tz = timezone(timedelta(hours=tz_offset))
  image = Image.new('RGB', (WIDTH, HEIGHT), COLOR_WHITE)
  draw = ImageDraw.Draw(image)
  
  # Context for drawing functions
  draw_context = {
    'ts': ts,
    'earth': earth,
    'moon': moon,
    'sun': sun,
    'draw': draw,
  }

  # Draw year text
  draw.text(
    (WIDTH // 2, PADDING),
    text=str(year),
    font=ImageFont.truetype(FONT_NAME, FZ_YEAR),
    fill=COLOR_BLACK,
    anchor='mt',
  )

  # Generate calendar data (4 months per row)
  data = calendar.Calendar(calendar.SUNDAY).yeardatescalendar(year, 4)
  # data structure: [row[month[week[day]]]]

  # Calculate month-specific spacing
  dgap = FZ_MONTH + FZ_WEEK + DGAP_OFFSET

  for r_index, row in enumerate(data):
    for m_index, month in enumerate(row):
      month_index = m_index + (r_index * 4) + 1
      month_name = calendar.month_name[month_index]

      BOX_POSITION_X1 = PADDING + (m_index * WGAP) + (m_index * WSPACE)
      BOX_POSITION_Y1 = PSTART + (r_index * HSPACE)
      BOX_POSITION_X2 = BOX_POSITION_X1 + WSPACE
      BOX_POSITION_Y2 = BOX_POSITION_Y1 + HSPACE

      # Draw month name
      draw.text(
        (BOX_POSITION_X2 - (WSPACE // 2), BOX_POSITION_Y1 - 20),
        text=month_name,
        font=ImageFont.truetype(FONT_NAME, FZ_MONTH),
        fill=COLOR_BLACK,
        anchor='mt',
      )

      # Draw weekday abbreviations
      for a_index, abbr in enumerate(WEEKDAY_LIST):
        draw.text(
          (
            BOX_POSITION_X1 + (ASPACE * a_index) + (ASPACE // 2),
            BOX_POSITION_Y1 + FZ_MONTH,
          ),
          text=abbr,
          font=ImageFont.truetype(FONT_NAME, FZ_WEEK),
          fill=COLOR_BLACK,
          anchor='mt',
        )

      # Draw separator line between header and dates
      draw.line(
        (
          BOX_POSITION_X1,
          BOX_POSITION_Y1 + FZ_MONTH + FZ_WEEK,
          BOX_POSITION_X2,
          BOX_POSITION_Y1 + FZ_MONTH + FZ_WEEK,
        ),
        fill=COLOR_BLACK,
        width=3,
      )

      for w_index, weekday in enumerate(month):
        DATE_POSITION_Y1 = BOX_POSITION_Y1 + dgap + (w_index * BGAP)
        DATE_POSITION_Y2 = DATE_POSITION_Y1 + BGAP

        for d_index, date in enumerate(weekday):
          DATE_POSITION_X1 = BOX_POSITION_X1 + (d_index * ASPACE)
          DATE_POSITION_X2 = DATE_POSITION_X1 + ASPACE

          if date.month != month_index:
            continue

          # Highlight weekend cells
          if d_index in (0, 6):
            draw.rectangle(
              (
                DATE_POSITION_X1,
                DATE_POSITION_Y1,
                DATE_POSITION_X2,
                DATE_POSITION_Y2,
              ),
              fill=COLOR_GRAY_LIGHT,
            )

          # Draw moon phase ring
          date_with_tz = datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            tzinfo=tz,
          )
          draw_moon_ring(
            DATE_POSITION_X1 + (ASPACE // 2),
            DATE_POSITION_Y1 + 33,
            30,
            date_with_tz,
            draw_context,
          )

          # Determine day text color (red for Sunday, blue for Saturday)
          date_color = COLOR_BLACK
          if d_index == 0:
            date_color = COLOR_RED
          elif d_index == 6:
            date_color = COLOR_BLUE

          # Draw day number
          draw.text(
            (
              DATE_POSITION_X1 + (ASPACE // 2),
              DATE_POSITION_Y1 + (FZ_WEEK // 2),
            ),
            text=str(date.day),
            font=ImageFont.truetype(FONT_NAME, FZ_WEEK),
            fill=date_color,
            anchor='mt',
          )

  # Save the generated calendar
  image.save("calendar.png")


if __name__ == "__main__":
  # Parse command-line arguments
  parser = argparse.ArgumentParser(description='Generate a calendar with moon phases')
  parser.add_argument('--tz', type=int, default=0, help='Timezone offset in hours (default: 0 for UTC)')
  parser.add_argument('--year', type=int, default=datetime.now().year, help=f'Year to generate calendar for (default: {datetime.now().year})')
  args = parser.parse_args()

  generate_calendar(tz_offset=args.tz, year=args.year)
