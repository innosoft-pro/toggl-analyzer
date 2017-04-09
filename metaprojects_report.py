#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export detailed report on metaprojects in JSON using Toggl API
"""
import datetime
import json
import pandas as pd

from toggl import Toggl
import settings


class MetaProject:
    def __init__(self):
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
        self.df = pd.DataFrame(reports)

        for_json = {
            'labels': None,
            'projects': [],
            'users': []
        }
        self.df['start'] = pd.to_datetime(self.df['start'])

    def get_total_weekly_data(self):
        return self.df.groupby(self.df.set_index('start').index.week).sum()

    def get_weekly_data_for_project(self, project):
        project_data = self._get_prject_data(project)
        return project_data.groupby(project_data.set_index('start').index.week).sum()

    def get_weekly_data_per_person(self, user):
        user_data = self._get_person_data(user)
        return user.groupby(user_data.set_index('start').index.week).sum()

    def _get_prject_data(self, project):
        return self.df.loc[self.df['project'] == project]

    def _get_person_data(self, user):
        return self.df.loc[self.df['user'] == user]

if __name__ == '__main__':


    # print(df.head())

    project_daily = df.set_index('start').groupby('project').resample(
        '1D').sum()  # overal time spent on a project day-by-day
    user_daily = df.set_index('start').groupby('user').resample('1D').sum()  # time spent by employee day-by-day
    dti = project_daily.index.get_level_values(1).unique().sort_values()
    date_labels = dti.map(lambda x: str(x.date())).tolist()  # date strings to label points on a chart

    for_json['labels'] = date_labels
    for project in project_daily.index.get_level_values(0).unique():
        for_json['projects'].append({
            'name': project,
            'data': project_daily.loc[project]['duration'].values.tolist()
        })
    # json.dumps(project_daily.loc[u"Минимакс"]['duration'].values.tolist())
    for user in user_daily.index.get_level_values(0).unique():
        for_json['users'].append({
            'name': user,
            'data': user_daily.loc[user]['duration'].values.tolist()
        })

    # print(json.dumps(reports))
    with open('data.js', 'w') as fp:
        s = "var data = %s;" % json.dumps(for_json)
        fp.write(s)
