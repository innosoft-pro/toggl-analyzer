#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Export detailed report on metaprojects in JSON using Toggl API
"""
import datetime
import json
import pandas as pd

from toggl import Toggl
import settings


if __name__ == '__main__':
    # timeframe for report
    end_date = datetime.datetime.now()
    start_date = end_date - settings.timeframe

    # create report
    report_builder = Toggl(settings.api_token)
    workspaces = report_builder.get_workspaces()

    reports = []

    for ws_name, ws_id in workspaces:
        if ws_name in settings.workspace2meta.keys():
            metaproject = settings.workspace2meta[ws_name]

            for record in report_builder.detailed_report(ws_id, start_date, end_date):
                # record duration is in milliseconds
                # divide by 3600000 to convert to hours
                reports.append({
                    'user': record['user'],
                    'team': ws_name,
                    'project': metaproject,
                    'subproject': record['project'],
                    # example of record['start']: 2015-05-29T16:07:20+03:00
                    'start': record['start'][:19],
                    'duration': round(float(record['dur']) / 3600000, 2)
                })

    for_json = {
        'labels': None,
        'projects': [],
        'users': []
    }
    df = pd.DataFrame(reports)
    # print(df.head())
    df['start'] = pd.to_datetime(df['start'])
    project_weekly = df.set_index('start').groupby('project').resample('1W').sum() # overal time spent on a project week-by-week
    user_weekly    = df.set_index('start').groupby('user').resample('1W').sum()    # time spent by employee week-by-week
    dti = project_weekly.index.get_level_values(1).unique().sort_values()
    date_labels = dti.map(lambda x: str(x.date())).tolist() # date strings for labeling points on a chart

    for_json['labels'] = date_labels
    for project in project_weekly.index.get_level_values(0).unique():
        for_json['projects'].append({
            'name': project,
            'data': project_weekly.loc[project]['duration'].values.tolist()
        })
    # json.dumps(project_weekly.loc[u"Минимакс"]['duration'].values.tolist())
    for user in user_weekly.index.get_level_values(0).unique():
        for_json['users'].append({
            'name': user,
            'data': user_weekly.loc[user]['duration'].values.tolist()
        })

    # print(json.dumps(reports))
    with open('data.js', 'w') as fp:
        s = "var data = %s;" % json.dumps(for_json)
        fp.write(s)
