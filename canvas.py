import requests
import sys
import datetime
from workflow import Workflow, ICON_WARNING, ICON_ERROR

def get_object(objectType, maxAge, url, arg1):  # one function for all object types
  object1 = wf.cached_data("%s-%s" % (arg1, objectType), max_age=maxAge)  # objectType and arg1 only determine cache location; no effect on URL

  if (not object1):
    response = requests.get(url, headers={"Authorization": "Bearer %s" % ACCESS_TOKEN})
    object1 = response.json()
    wf.cache_data("%s-%s" % (arg1, objectType), object1)
  
  return object1

def get_courses():  # list favorite courses
  response = requests.get("https://%s/api/v1/users/self/favorites/courses" % (URL), headers={"Authorization": "Bearer %s" % ACCESS_TOKEN})
  return response.json()  # returns list of course objects
  
# ~~~~~~~~~~OBSOLETE~~~~~~~~~~
def get_modules(courseID):
  response = requests.get("https://%s/api/v1/courses/%s/modules?access_token=%s" % (URL, courseID, ACCESS_TOKEN))
  return response.json()

def get_module_items(courseID, moduleID):
  response = requests.get("https://%s/api/v1/courses/%s/modules/%s/items?access_token=%s" % (URL, courseID, moduleID, ACCESS_TOKEN))
  return response.json()

def get_sections(courseID):
  response = requests.get("https://%s/api/v1/courses/%s/sections?access_token=%s" % (URL, courseID, ACCESS_TOKEN))
  return response.json()

def get_tabs(courseID):  # obsolete
  tabs = wf.cached_data("%s-tabs" % courseID, max_age=1200)

  if (not tabs):
    tabs = requests.get("https://%s/api/v1/courses/%s/tabs?access_token=%s" % (URL, courseID, ACCESS_TOKEN))
    tabs = tabs.json()
    wf.cache_data("%s-tabs" % courseID, tabs)
  return tabs

def get_assignments(courseID):
  response = requests.get("https://%s/api/v1/courses/%s/assignments?access_token=%s&order_by=due_at&include[]=submission" % (URL, courseID, ACCESS_TOKEN))
  return response.json()

def get_announcements(courseID):
  response = requests.get("https://%s/api/v1/announcements?context_codes[]=course_%s&access_token=%s" % (URL, courseID, ACCESS_TOKEN))
  return response.json()

def get_submission(courseID, assignmentID):
  response = requests.get("https://%s/api/v1/courses/%s/assignments/%s?access_token=%s" % (URL, courseID, assignmentID, ACCESS_TOKEN))
  return response

def get_page(courseID, pageURL):
  response = requests.get("https://%s/api/v1/courses/%s/pages/%s?access_token=%s" % (URL, courseID, pageURL, ACCESS_TOKEN))
  return response.json()

def get_files(courseID):
  response = requests.get("https://%s/api/v1/courses/%s/files?access_token=%s" % (URL, courseID, ACCESS_TOKEN))
  return response.json()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_file_from_id(courseID, fileID):  # get file object from module id
  file1 = wf.cached_data("%s-file" % fileID, max_age=172800)  # file object

  if (not file1):
    file1 = requests.get("https://%s/api/v1/courses/%s/files/%s?access_token=%s" % (URL, courseID, fileID, ACCESS_TOKEN))
    file1 = file1.json()
    wf.cache_data("%s-file" % fileID, file1)

  return file1

def remove_html(text):
  new_text = text.replace('<p>', '').replace('</p>', '').replace('<br>', '')  # remove basic formatting

  letters = ""  # remove more complicated formatting
  for letter in new_text:
    if (letter == ">"):
      letters += letter
      new_text = new_text.replace(letters, '')
      letters = ""
    elif (letter == "<" or len(letters) > 0): letters += letter
    
  return new_text

def get_links(text):  # returns list of links
  letters = ""
  link = [""]
  text = text.replace(u'\xa0', u' ')
  getDescription = False
  description = ""

  for letter in text:
    if ((letter == '"' or letter == " " or letter == "\n" or letter == "<") and letters != "href=" and letters != "src="):
      letters = ""
      getDescription = False
      if (link[-1] != ""):
        link.append("")
        getDescription = True
      # print("Letters cleared.")
    elif (letters == 'href="' or letters == 'src="'):
      link[-1] += letter
      # print("Link: %s" % link)
    # elif (letter == "h" len(letters) > 0):
    else:
      letters += letter
      if (getDescription and (letter != ">")): description += letter
      # print("Letters: %s" % letters)

  # print(link)
  if (link[-1] == ""): link.pop(-1)

  # print(description)
  return link

def remove_duplicates(list1):  # remove duplicates from list
  newList = list1
  for item in newList:
    if (newList.count(item) > 1): newList.remove(item)
  return newList

def main(wf):

  if (len(query) and query[0] == "!"):
    command = query.split(" ")[0]
    arg = query[len(command) + 1:]
    argList = query.split(" ")[1:]

    log.debug("argList: %s" % argList)

    if (argList == []): argList.append("")  # fix some cases where user may not have finished typing

    if (command == "!get_tabs"):
      search = "".join(argList[1:])

      tabs = get_object(objectType="tabs", maxAge=1200, url="https://%s/api/v1/courses/%s/tabs" % (URL, argList[0]), arg1=argList[0])

      def key_for_tab(tab):
        return u'{}'.format(tab['label'].replace(u'\xa0', u' '), min_score=64)

      tabs = wf.filter(search, tabs, key_for_tab)

      for tab in tabs: 
        if (tab[u'id'] == "home"): wf.add_item(title=tab[u'label'], subtitle="Select this action to open the homepage in your browser.", valid=True, arg="!open_url https://%s%s" % (URL, tab[u'html_url']), icon="icons/link.png")
        elif (tab[u'id'] == "modules" or tab[u'id'] == "assignments" or tab[u'id'] == "announcements" or tab[u'id'] == "files"): wf.add_item(title=tab[u'label'], valid=True, arg="!get_%s %s " % (tab[u'id'].lower(), argList[0]), icon="icons/%s.png" % tab[u'id'].lower())

    elif (command == "!get_files"):
      search = "".join(argList[1:])

      files = get_object(objectType="files", maxAge=60, url="https://%s/api/v1/courses/%s/files" % (URL, argList[0]), arg1=argList[0])

      def key_for_file(file1):
        return u'{} {}'.format(file1['display_name'].replace(u'\xa0', u' '), file1['filename'].replace(u'\xa0', u' '), min_score=64)

      files = wf.filter(search, files, key_for_file)

      for file1 in files: wf.add_item(title=file1['display_name'].replace(u'\xa0', u' '), subtitle=file1['url'], valid=True, arg="!open_url %s" % file1[u'url'], icon="icons/assignment.png")

    elif (command == "!get_page"):
      page = get_object(objectType="page", maxAge=120, url="https://%s/api/v1/courses/%s/pages/%s" % (URL, argList[0], argList[1]), arg1=argList[1])

      links = remove_duplicates(get_links(page[u'body']))

      if (remove_html(page[u'body']) == ''): page[u'body'] = "Page is empty."

      if (page):
        wf.add_item(title="Show full page", subtitle=remove_html(page[u'body']), valid=True, arg="Description:\n\n %s" % remove_html(page[u'body']), icon="icons/info.png")

        for item in links:
          wf.add_item(title="Open link", subtitle=item, valid=True, arg="!open_url %s" % item, icon="icons/link.png")

        wf.add_item(title="Open page", subtitle="https://%s/courses/%s/pages/%s" % (URL, argList[0], page[u'url']), valid=True, arg="!open_url https://%s/courses/%s/pages/%s" % (URL, argList[0], page[u'url']), icon="icons/link.png")
    
    elif (command == "!get_announcements"):
      search = "".join(argList[1:])
      log.debug("Getting announcements...")
      announcements = get_object(objectType="announcements", maxAge=60, url="https://%s/api/v1/announcements?context_codes[]=course_%s&per_page=50" % (URL, argList[0]), arg1=argList[0])

      def key_for_announcement(announcement):
        return u'{} {}'.format(announcement['title'], remove_html(announcement['message']), min_score=64)

      announcements = wf.filter(search, announcements, key_for_announcement)

      if (announcements):
        for announcement in announcements: wf.add_item(title=announcement[u'title'], subtitle="Posted at: %s" % announcement[u'posted_at'], valid=True, arg="!get_announcement %s %s" % (argList[0], announcement[u'id']), icon="icons/announcements.png")
      else:
        wf.add_item(title="No announcements match your search", icon=ICON_WARNING)

    elif (command == "!get_announcement"):
      announcements = get_object(objectType="announcements", maxAge=60, url="https://%s/api/v1/announcements?context_codes[]=course_%s" % (URL, argList[0]), arg1=argList[0])

      announcement = {}
      for item in announcements:
        if (str(item[u'id']) == str(argList[1])): announcement = item

      links = remove_duplicates(get_links(announcement[u'message']))

      if (announcement != {}):
        wf.add_item(title="Show full message", subtitle=remove_html(announcement[u'message']), valid=True, arg="Message: \n\n%s" % remove_html(announcement[u'message']), icon="icons/info.png")

        for item in links:
          wf.add_item(title="Open link", subtitle=item, valid=True, arg="!open_url %s" % item, icon="icons/link.png")

        wf.add_item(title="Open announcement page", subtitle="https://%s/courses/%s/announcements/%s" % (URL, argList[0], argList[1]), valid=True, arg="!open_url https://%s/courses/%s/announcements/%s" % (URL, argList[0], argList[1]), icon="icons/link.png")
    
    elif (command == "!get_modules"):
      search = "".join(argList[1:])

      modules = get_object(objectType="modules", maxAge=60, url="https://%s/api/v1/courses/%s/modules?per_page=100" % (URL, argList[0]), arg1=argList[0])

      def key_for_module(module):
        return u'{}'.format(module['name'], min_score=64)

      modules = wf.filter(search, modules, key_for_module)

      for module in modules: wf.add_item(title=module[u'name'], valid=True, arg="!get_module_items %s %s " % (str(argList[0]), str(module[u'id'])), icon="icons/modules.png")

    elif (command == "!get_module_items"):
      search = "".join(argList[2:])

      items = get_object(objectType="items", maxAge=60, url="https://%s/api/v1/courses/%s/modules/%s/items?per_page=100" % (URL, argList[0], argList[1]), arg1=argList[1])

      def key_for_item(item):
        return u'{}'.format(item['title'], min_score=64)

      items = wf.filter(search, items, key_for_item)

      for item in items: 
        if (item[u'type'] == "ExternalUrl" or item[u'type'] == "ExternalTool"): wf.add_item(title=item[u'title'], subtitle=str(item[u'external_url']), valid=True, arg="!open_url %s" % item[u'external_url'], icon="icons/link.png")
        elif (item[u'type'] == "File"): wf.add_item(title=item[u'title'], subtitle=str(item[u'type']), valid=True, arg="!open_url %s" % get_file_from_id(argList[0], item[u'content_id'])[u'url'], icon="icons/files.png")
        elif (item[u'type'] == "Assignment"): wf.add_item(title=item[u'title'], subtitle=str(item[u'type']), valid=True, arg="!get_%s %s %s" % (item[u'type'].lower(), argList[0], item[u'content_id']), icon="icons/%s.png" % (item[u'type'].lower()))
        elif (item[u'type'] == "Page"): wf.add_item(title=item[u'title'], subtitle=str(item[u'type']), valid=True, arg="!get_%s %s %s " % (item[u'type'].lower(), argList[0], item[u'page_url']), icon="icons/%s.png" % (item[u'type'].lower()))
        else: wf.add_item(title=item[u'title'], subtitle=str(item[u'type']), valid=True, arg="!open_url %s" % item[u'html_url'], icon="icons/%s.png" % item[u'type'].lower())

    elif (command == "!get_module_item"):  # obsolete
      items = wf.cached_data("%s-items" % argList[0], max_age=60)

      if (not items):
        items = get_module_items(argList[0], argList[1])
        wf.cache_data("%s-items" % argList[1], items)

      moduleItem = {}
      for item in items:
        if (str(item[u'id']) == str(argList[1])): moduleItem = item

      if (moduleItem != {}):
        wf.add_item(title="Open module page", subtitle=module[u'html_url'], valid=True, arg="!open_url %s" % item[u'html_url'], icon="icons/link.png")

    elif (command == "!get_sections"):
      sections = get_sections(arg)
      for section in sections: wf.add_item(section[u'name'])
 
    elif (command == "!get_assignments"):
      search = "".join(argList[1:])

      assignments = get_object("assignments", 60, "https://%s/api/v1/courses/%s/assignments?order_by=due_at&include[]=submission&per_page=500" % (URL, argList[0]), argList[0])

      def key_for_assignment(assignments):
        return u'{}'.format(assignments[u'name'], min_score=64)

      assignments = wf.filter(search, assignments, key_for_assignment)
      
      for assignment in assignments: wf.add_item(title=assignment[u'name'], valid=True, arg="!get_assignment %s %s" % (argList[0], str(assignment[u'id'])), icon="icons/assignments.png")


    elif (command == "!get_assignment"):
      assignments = wf.cached_data("%s-assignments" % argList[0], max_age=300)

      if (not assignments):
        assignments = get_assignments(argList[0])
        wf.cache_data("%s-assignments" % argList[0], assignments)

      assignment = {}
      for item in assignments:
        if (str(item[u'id']) == str(argList[1])): assignment = item

      if (assignment != {}):
        submission = assignment[u'submission']
        submissionText = ""
        submissionArg = ""
        submissionIcon = "icons/unsubmitted.png"

        if (submission["workflow_state"] == "unsubmitted"):
          submissionText = "Due at: %s   Locks at: %s" % (str(assignment["due_at"]), str(assignment["lock_at"]))
        elif (submission["workflow_state"] == "submitted"):
          submissionText = "Submitted at: %s" % submission["submitted_at"]
          submissionIcon = "icons/submitted.png"

        links = remove_duplicates(get_links(assignment[u'description']))

        wf.add_item(title="Show full description", subtitle=remove_html(assignment[u'description']), valid=True, arg="Description: \n\n%s" % remove_html(assignment[u'description']), icon="icons/info.png")
        
        for item in links:
          wf.add_item(title="Open link", subtitle=item, valid=True, arg="!open_url %s" % item, icon="icons/link.png")

        wf.add_item(title="Submission status: %s" % str(submission[u'workflow_state']), subtitle=submissionText, valid=True, arg="!copy %s" % str(submission), icon=submissionIcon)
        wf.add_item(title="Open assignment page", subtitle=assignment[u'html_url'], valid=True, arg="!open_url %s" % assignment[u'html_url'], icon="icons/link.png")

      else:
        wf.add_item(title="Invalid assignment or course ID.", subtitle="Please try again using a different assignment or course ID.")

    elif (command == "!set_url"):
      wf.add_item(title="Set Canvas URL to https://%s" % argList[0], subtitle="Current URL: https://%s" % str(URL), valid=True, arg="!url_set %s" % argList[0], icon="icons/link.png")
    
    elif (command == "!url_set"):
      wf.store_data("url", argList[0])
      wf.clear_cache()  # force update cache with new URL

    elif (command == "!clear_cache"):
      wf.clear_cache()  # debugging only
      wf.add_item(title="Cache cleared.")

    elif (command == "!save_api_key"):
      wf.add_item(title="Paste access token here", subtitle="Press ENTER to save your access token.", valid=True, arg="!api_key_save %s" % str(argList[0]), icon="icons/settings.png")
    
    elif (command == "!api_key_save"):
      wf.save_password("api-key", str(argList[0]))
      wf.clear_cache()  # force update cache with new API data

    else:
      listCommands = [{u"name": "!set_url",
                       u"description": u"Set the custom Canvas URL used by your district or institution."},
                      {u"name": "!clear_cache",
                       u"description": u"Clear all cached data. Useful when debugging."},
                      {u"name": "!save_api_key",
                       u"description": u"Save the access key generated in Canvas."}]

      def key_for_command(command):
        return "{}".format(command[u'name'], min_score=64)
      
      hits = wf.filter(command, listCommands, key_for_command)

      for item in hits: wf.add_item(title=item[u'name'], subtitle=item[u'description'], valid=True, arg="%s " % item[u'name'], icon="icons/settings.png")
    
  else:
    courses = wf.cached_data("courses", get_courses, max_age=1200)

    def key_for_course(course):
      return "{}".format(course[u'name'], min_score=64)

    courses = wf.filter(query, courses, key_for_course)

    for item in courses:
      try: wf.add_item(title=item[u'name'], valid=True, arg="!get_tabs %s " % item[u'id'], icon="icons/study.png")
      except:
        wf.add_item(title="An error occurred while updating courses.", subtitle="Is your access key correct? Use !save_api_key to update your access key.", icon=ICON_ERROR, valid=True, arg="!save_api_key ")

  wf.send_feedback()
  return 0

if (__name__ == "__main__"):
  wf = Workflow(libraries=['./lib'])

  if (len(wf.args)):
    query = wf.args[0]

  URL = wf.stored_data('url')
  if (not URL):
    URL = "canvas.instructure.com"
    wf.store_data('url', "canvas.instructure.com")

  if (query[0:13] != "!save_api_key" and query[0:13] != "!api_key_save"):
    try: ACCESS_TOKEN = wf.get_password("api-key")
    except:
      wf.add_item(title="API key not found.", subtitle="Select this action to get your access token.", valid=True, arg="!open_url https://%s/profile/settings" % URL)
      wf.add_item(title="Enter API key", subtitle="Select this action when you're ready to paste your API key.", valid=True, arg="!save_api_key ")
      wf.send_feedback()
      sys.exit(0)

  log = wf.logger
  sys.exit(wf.run(main))