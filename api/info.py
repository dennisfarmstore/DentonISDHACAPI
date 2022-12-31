from http.server import BaseHTTPRequestHandler
from bs4 import BeautifulSoup
import json
import lxml
import cchardet
from urllib import parse

from _lib.getRequestSession import getRequestSession
from _lib.fakeData import fakeStudentInfo

class handler(BaseHTTPRequestHandler):

  def do_GET(self):
    dic = dict(parse.parse_qsl(parse.urlsplit(self.path).query))

    username = dic["username"]
    password = dic["password"]

    if(username.lower() == "john" and password.lower() == "doe"):
      self.send_response(200)
      self.send_header('Content-type', 'application/json')
      self.end_headers()
      self.wfile.write(json.dumps(fakeStudentInfo).encode(encoding="utf_8"))

      return

    session = getRequestSession(username, password)

    registrationPageContent = session.get("https://hac.friscoisd.org/HomeAccess/Content/Student/Registration.aspx").text

    parser =  BeautifulSoup(registrationPageContent, "lxml")

    studentName = parser.find(id="plnMain_lblRegStudentName").text
    studentBirthdate = parser.find(id="plnMain_lblBirthDate").text
    studentCounselor = parser.find(id="plnMain_lblCounselor").text
    studentCampus = parser.find(id="plnMain_lblBuildingName").text
    studentGrade = parser.find(id="plnMain_lblGrade").text

    # Try to get the student id from the registration page
    # If this fails, try to get the student id from the student schedule page
    # Thank you @AniruddhAnand for this
    try:
      studentId = parser.find(id="plnMain_lblRegStudentID").text
    except:
      schedulePageContent = session.get("https://hac.friscoisd.org/HomeAccess/Content/Student/Classes.aspx")
      parser =  BeautifulSoup(schedulePageContent, "lxml")
      studentId = parser.find(id="plnMain_lblRegStudentID").text

    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps({
      "id": studentId,
      "name": studentName,
      "birthdate": studentBirthdate,
      "campus": studentCampus,
      "grade": studentGrade,
      "counselor": studentCounselor
    }).encode(encoding="utf_8"))

    return
