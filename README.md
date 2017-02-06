# Simple Toggl HTML report generator

Generates graphs of daily time logged per project and per user.
Projects might span several workspaces so we call them metaprojects to distinguish from Toggl projects.


## Configuration

The generator is configured through `settings.py` file.
First of all you must get your Toggl API token and put it into
```py
api_token = '<Toggl API token>'
```
Without API token nothing will work.

Besides you might configure number of days to generate report for:
```py
timeframe = datetime.timedelta(days=30)
```
This parameter heavily affects running time.

Finally you should specify mapping from workspaces to metaprojects. It might be
one-to-one or many-to-one mapping. Technically nothing prevents you from specifying
one-to-many mapping but I bet this will mess all things up. Correct config looks like this:
```py
workspace2meta = {
    'YORSO': 'YORSO',
    'YORSO2': 'YORSO',
    u"Минимакс": u"Минимакс"
}
```
Only workspaces mentioned in the mapping get processed.


## Usage

```
$ python2 metaprojects_report.py
```

Then open `charts.html` in your favorite web-browser.
