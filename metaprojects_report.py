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
        self.df['start'] = pd.to_datetime(self.df['start'])
        self.first_timestamp = self.df.min(axis=1)
        self.projects = list(self.df.set_index('project').index.get_level_values(0).unique())
        self.users = list(self.df.set_index('user').index.get_level_values(0).unique())

    def get_total_weekly_data(self):
        res = self.df.groupby(self.df.set_index('start').index.week).sum().to_dict(orient='split')
        mondays_list = [(datetime.datetime.strptime(
            settings.start_date.split('-')[0] + "-W" + str(week_number) + '-1', "%Y-W%W-%w")
                        ).strftime('%Y-%m-%d') for week_number in res['index']]
        return mondays_list

    def get_weekly_data_for_project(self, project):
        project_data = self._get_project_data(project)
        return project_data.groupby(project_data.set_index('start').index.week).sum().to_dict()

    def get_weekly_data_per_person(self, user):
        user_data = self._get_person_data(user)
        return user.groupby(user_data.set_index('start').index.week).sum().to_dict()

    def get_weekly_project_per_person(self, project):
        project_data = self._get_project_data(project)
        result_data = dict()
        for user in self.users:
            filtered_by_user = project_data.loc[project_data['user'] == user]
            one_user_data = filtered_by_user.groupby(filtered_by_user.set_index('start').
                                                     index.week).sum().to_dict(orient='list')
            result_data[user] = [item if item else None for item in one_user_data['duration']]
        return result_data

    def get_weekly_project_per_person_avg(self, project):
        project_data = self._get_project_data(project)
        result_data = dict()
        for user in self.users:
            filtered_by_user = project_data.loc[project_data['user'] == user]
            one_user_data = filtered_by_user.groupby(filtered_by_user.set_index('start').
                                                     index.week).sum().to_dict(orient='list')
            result_data[user] = sum(one_user_data['duration']) / float(len(one_user_data['duration'])
                                                                       if len(one_user_data['duration']) else 1)
        return result_data

    def _get_project_data(self, project):
        return self.df.loc[self.df['project'] == project]

    def _get_person_data(self, user):
        return self.df.loc[self.df['user'] == user]


if __name__ == '__main__':
    metaproject = MetaProject()
    projects = metaproject.projects
    users = metaproject.users

    resulting_json = {
        "week_labels": metaproject.get_total_weekly_data(),
        "projects": projects,
        "users": users,
        "data": {project: metaproject.get_weekly_project_per_person(project) for project in projects},
        "avg": {project: metaproject.get_weekly_project_per_person_avg(project) for project in projects}
    }

    with open('data.js', 'w') as fp:
        week_labels = 'var labels = {};'.format(json.dumps(resulting_json["week_labels"]))
        data = 'var data = {};'.format(json.dumps(resulting_json["data"]))
        user = 'var users = {};'.format(json.dumps(resulting_json["users"]))
        projects = 'var projects = {};'.format(json.dumps(resulting_json["projects"]))
        timestamp = 'var init_time = "{}";'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        avg = 'var avg = {};'.format(resulting_json['avg'])
        fp.write(week_labels)
        fp.write(data)
        fp.write(user)
        fp.write(projects)
        fp.write(timestamp)
        fp.write(avg)
