# Reporter

Reporter is a CLI-tool that allows the user to generate Latex tabulars from several .csv log files which 
reflect access statistics of different countries on a server.

## Usage
Generate a report beginning at the first date of the current month until current day.

```bash
python3 reporter.py
```

Generate a report over all available log files.

```bash
python3 reporter.py --full
```

Generate a report beginning at the first date of the current month until a specified day.
```bash
python3 reporter.py --end 20XX-XX-XX
```

Generate a report beginning at a specified date until the current day.
```bash
python3 reporter.py --start 20XX-XX-XX
```

Generate a report for a whole month (1-12)
```bash
python3 reporter.py --month 3
```
