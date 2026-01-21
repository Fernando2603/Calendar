# Calendar
A Python script that generates a customizable calendar with moon phases for any year and timezone using GitHub Actions.

## Features
- Moon phase visualization for each day
- Moon illumination circles with phase indicators
- Lunar calendar integration (new moon and full moon highlighting)
- Weekday coloring (red for Sunday, blue for Saturday)
- Customizable timezone and year
- High-resolution A4-sized output (3508x2480px at 300dpi)

## Usage
### GitHub Actions Workflow
Generate calendars using the GitHub Actions workflow:

1. Go to your repository's **Actions** tab
2. Select **Generate Calendar** workflow
3. Click **Run workflow**
4. Enter the optional parameters:
   - **year**: Leave empty for current year, or specify a year (e.g., `2025`)
   - **timezone**: Timezone offset in hours (default: `0` for UTC)
5. Click **Run workflow**

The generated calendar will be available as an artifact for download.

### Examples
- **Current year, UTC**: Leave both fields empty
- **2025, UTC+7**: Set `year: 2025`, `timezone: 7`
- **2026, UTC-5**: Set `year: 2026`, `timezone: -5`

### Timezone Offsets
Common timezone offsets:
- **UTC**: 0
- **India Standard Time (IST)**: +5.5 (or use 5 for UTC+5)
- **China Standard Time (CST)**: +8
- **Japan Standard Time (JST)**: +9
- **Eastern Standard Time (EST)**: -5
- **Pacific Standard Time (PST)**: -8

## Output
The workflow generates a calendar image as `calendar.png` and uploads it as a GitHub Actions artifact that can be downloaded for 30 days.
