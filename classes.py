from stravalib import Client
from datetime import datetime, timedelta
from toggl.TogglPy import Toggl
from boto.s3.connection import S3Connection

class Strava():

    def __init__(self):
        self.client = Client()
        self.url = self.client.authorization_url(client_id=41952,
                                                 redirect_uri='http://127.0.0.1:5000/authorization')

    def get_access_token(self, code):
        self.code = code
        try:
            with open("secrets.txt", 'r') as f:
                clientid = f.readlines()
                print(clientid)
        except:
            s3 = S3Connection(os.environ['client_id'], os.environ['client_secret'])
        self.access_token = self.client.exchange_code_for_token(client_id=clientid[0],
                                                                client_secret=clientid[1],
                                                                code=self.code)
        self.access_token = self.access_token['access_token']
        self.client = Client(access_token=self.access_token)
        return self.access_token

    def get_activities(self, days, code):
        dt1 = datetime.now()
        dt2 = timedelta(days=days)
        dt3 = dt1 - dt2
        dt3 = dt3.strftime("%Y-%m-%dT%H:%M:%SZ")
        client = Client(access_token=code)
        activities = client.get_activities(after=dt3)
        return activities

class Toggls():

    def __init__(self, key):
        self.toggl = Toggl()
        self.toggl.setAPIKey(key)

    def get_Workspaces(self):
        return self.toggl.getWorkspaces()

    def getprojectsinworkspace(self, id):
        urls = "https://www.toggl.com/api/v8/workspaces/" + str(id) + "/projects"
        return self.toggl.request(urls)

    def get_workspace(self, name):
        return self.toggl.getWorkspace(name)

    def make_time_entry(self, pid, workout):
        start = workout[1][6:10] + "-" + workout[1][:2] + "-" + workout[1][3:5] + "T" + workout[1][12:] + ".000Z"
        time = float(workout[2][0])*60*60 + float(workout[2][2:4])*60 + float(workout[2][5:7])
        url = 'https://www.toggl.com/api/v8/time_entries'
        data = {
            "time_entry":
                {
                    "description":"Workout",
                    "tags":[""],
                    "duration": time,
                    "start": start,
                    "pid": pid,
                    "created_with":"api"
                }
        }
        return self.toggl.postRequest(url, parameters=data)


if __name__ == '__main__':
    tog = Toggls()
    workout = ['Lunch Walk', '02/17/2020, 19:46:16', '0:34:01']
    pid = 157263501
    start = workout[1][6:10] + "-" + workout[1][:2] + "-" + workout[1][3:5] + "T" + workout[1][12:] + ".000Z"
    print(start)
    print(tog.make_time_entry(pid = 157263501, workout=workout))