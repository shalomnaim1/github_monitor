#!/bin/python

import json
from datetime import datetime
from github import Github 
from optparse import OptionParser, OptionGroup


class git_monitor(object):
    
    def __init__(self, username, password, repo_name):
        self.github_client =  Github(username, password)
        self.repo = self.github_client.get_repo(repo_name)

    def get_file_info(self, file_path, property_name):
        c = self.repo.get_file_contents(file_path)
        return  getattr(c, property_name, None)  
    
    def to_json(self, property_name, value):
        return json.dumps({property_name : value})
        
    def to_text(self, property_name, value):
        return f"{property_name}: {value}"
    
    def get_info(self, file_path, property_name, output_format):
        value = self.get_file_info(file_path, property_name)

        if output_format == "text":
            return self.to_text(property_name, value)
        elif output_format == "JSON":
            return self.to_json(property_name, value)
        else:
            raise Exception(f"Unknow format type {output_format}")

    def is_modefied_in_last_X_hours(self, file_path, property_name, diff):
        curr_time = datetime.now()
        diff_date = datetime.strptime(self.get_file_info(file_path, property_name), "%a, %d %b %Y %X %Z")
        td = diff_date - curr_time

        return td.seconds > diff * 3600

def get_optparser():
    parser = OptionParser()
    time_diff
    parser.add_option("-u", "--user", dest="username", help="GitHub username", type="string")
    parser.add_option("-p", "--passsword", dest="password", help="GitHub password", type="string")
    parser.add_option("-r", "--repo", dest="repository",help="GitHub reposotory name", type="string")
    parser.add_option("-f", "--file_path", type="string", help="Reqired file path in the repo")
    parser.add_option("-a", "--action", type="string", help="Action to do (get_info\\time_diff)")    

    get_info_group = OptionGroup(parser, "Get info", "Get info about specific item")
    get_info_group.add_option("-o", "--output_type", type="string", default="text", help="Output format (text\JSON)")
    get_info_group.add_option("-P", "--property", type="string",  help="Property name")
    
    time_diff_group = OptionGroup(parser, "Time diff", "Check time diff for some proprty")
    time_diff_group.add_option("-d", "--max_diff", type=int, default=1, help="max diff in hours")

    return parser

def main():
    parser = get_optparser()
    (options, args) = parser.parse_args()
    
    monitor_instance = git_monitor(options.username, options.password, options.repository)
    action_dict = {"get_info": monitor_instance.get_info, "time_diff": monitor_instance.is_modefied_in_last_X_hours}
    action_kwagrs = {"get_info" :{"property_name": "last_modified", 
                                  "file_path": options.file_path, 
                                  "output_format": options.output_type}, 
                     "time_diff":{"file_path": options.file_path, 
                                  "property_name": options.property, 
                                  "diff": options.max_diff}} 

    print(action_dict[options.action](**action_kwagrs[options.action]))
    #print(gm.is_modefied_latly("public/doc/swagger-2-v0.0.1.yaml", "last_modified", 1))

if __name__ == "__main__":
   main()
