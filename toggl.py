#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import logging
import base64


class Toggl(object):
    """ Class to access Toggl API

    API docs can be found at:
    https://github.com/toggl/toggl_api_docs/blob/master/reports.md
    """
    baseURL = 'https://toggl.com/'
    date_format = '%Y-%m-%d'  # YYYY-MM-DD

    def __init__(self, api_token):
        self.logger = logging.getLogger(__name__)
        self.api_token = base64.b64encode((api_token + ':api_token').encode()).decode('utf-8')

    def get_workspaces(self):
        """ Get workspaces list
        :returns 2-tuple list of workspaces: [(<name>, <id>), ...].
        """
        request = requests.get('https://toggl.com/api/v8/workspaces',
                               headers={'Authorization': 'Basic ' + self.api_token})

        # filter out personal workspaces:
        json_data = request.json()
        return [(data['name'], data['id']) for data in json_data]

    def get_workspace_users_emails(self, workspace_id):
        """ Get list of workspace user emails.
        :param workspace_id: toggle workspace id, obtained from get_workspaces
        :return: list of emails, e.g. ['john@acme.com', 'harry@acme.com', ...]

        More information on API call output:
        https://github.com/toggl/toggl_api_docs/blob/master/chapters/workspaces.md#get-workspace-users
        """
        request = requests.get('https://toggl.com/api/v8/workspaces/' + workspace_id + '/users',
                               headers={'Authorization': 'Basic ' + self.api_token})
        json_data = request.json()
        return [user['email'] for user in json_data]

    def get_projects(self, workspace_id):
        """ Get projects information
        :param workspace_id: toggle workspace id, obtained from get_workspaces
        :return: list of active project names for a given workspace

        More information on API call output:
        https://github.com/toggl/toggl_api_docs/blob/master/chapters/workspaces.md#get-workspace-projects
        """
        result_list = list()
        reply = requests.get('api/v8/workspaces/' + workspace_id + '/projects')
        for project in reply.json():
            if project['active']:
                result_list.append(project['name'])
        return result_list

    def weekly_report(self, workspace_id, since, until):
        """ Toggl weekly report for a given team """
        return self._request('reports/api/v2/weekly', {
            'workspace_id': workspace_id,
            'since': since.strftime(self.date_format),
            'until': until.strftime(self.date_format),
            'user_agent': 'github.com/user2589/Toggl.py',
            'order_field': 'title',
            # title/day1/day2/day3/day4/day5/day6/day7/week_total
            'display_hours': 'decimal',  # decimal/minutes
        })

    def detailed_report(self, workspace_id, since, until):
        """ Toggl detailed report for a given team

        More information on API call output:
        https://github.com/toggl/toggl_api_docs/blob/master/reports/detailed.md#example
        """
        page = 1
        records_read = 0
        records = []
        while True:
            report_page = self._request('reports/api/v2/details', {
                'workspace_id': workspace_id,
                'since': since.strftime(self.date_format),
                'until': until.strftime(self.date_format),
                'user_agent': 'github.com/user2589/Toggl.py',
                'order_field': 'date',
                # date/description/duration/user in detailed reports
                'order_desc': 'off',  # on/off
                'display_hours': 'decimal',  # decimal/minutes
                'page': page
            })
            records.extend(report_page['data'])

            records_read += report_page['per_page']
            page += 1

            if records_read >= report_page['total_count']:
                return records
