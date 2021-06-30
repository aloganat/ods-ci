# Script to generate test config file

import os
import argparse
import re
import subprocess
import shutil
import yaml

def parse_args():
    """Parse CLI arguments"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Script to generate test config file'
        )
    parser.add_argument("-u", "--gituser",
                        help="git username",
                        action="store", dest="git_username",
                        default="")
    parser.add_argument("-p", "--gitpassword",
                        help="git password",
                        action="store", dest="git_password",
                        default="")
    parser.add_argument("-r", "--gitrepo",
                        help="config git repo for ods-ci tests",
                        action="store", dest="git_repo",
                        default="https://gitlab.cee.redhat.com/aloganat/odhcluster.git")
    parser.add_argument("-b", "--gitRepoBranch",
                        help="config git repo branch for ods-ci tests",
                        action="store", dest="git_repo_branch",
                        default="update_cluster")
    parser.add_argument("-d", "--repoDir",
                        help="directory to clone the git repo",
                        action="store", dest="repo_dir",
                        default="configrepo")
    parser.add_argument("-c", "--configtemplate",
                        help="absolute path of test config yaml file template",
                        action="store", dest="config_template",
                        default="resources/configs/test-variables.yml")
    parser.add_argument("-t", "--testcluster",
                        help="polarion password",
                        action="store", dest="test_cluster",
                        required=True)
    return parser.parse_args()

def clone_config_repo(**kwargs):
    """
    """
    try:
       if os.path.exists(kwargs["repo_dir"]) and os.path.isdir(kwargs["repo_dir"]):
           shutil.rmtree(kwargs["repo_dir"])
       os.makedirs(kwargs["repo_dir"])
       print("git repo dir '%s' created successfully" % kwargs["repo_dir"])
    except OSError as error:
       print("git repo dir '%s' can not be created." % kwargs["repo_dir"])

    git_repo_with_credens = kwargs["git_repo"]
    if kwargs["git_username"] != "" and kwargs["git_password"] != "":
        git_credens = "{}:{}".format(kwargs["git_username"], kwargs["git_password"])
        git_repo_with_credens = re.sub(r'(https://)(.*)', r'\1' + git_credens + "@" + r'\2', kwargs["git_repo"])
    cmd = "git clone {} -b {} {}".format(git_repo_with_credens, kwargs["git_branch"], kwargs["repo_dir"])
    ret = subprocess.call(cmd, shell=True)
    if not ret:
        print("Failed to clone repo {}.".format(kwargs["git_repo"]))

def getConfigData(configFile):
    """
    """
    with open(configFile, 'r') as fh:
        return yaml.safe_load(fh)

def generate_test_config_file(config_template, config_data, test_cluster):
    """
    """
    shutil.copy(config_template, '.')
    config_file = os.path.basename(config_template)
    with open(config_file, 'r') as fh:
        data = yaml.safe_load(fh)

    data["BROWSER"]["NAME"] = config_data["BROWSER"]["NAME"]
    data["S3"]["AWS_ACCESS_KEY_ID"] = config_data["S3"]["AWS_ACCESS_KEY_ID"]
    data["S3"]["AWS_SECRET_ACCESS_KEY"] = config_data["S3"]["AWS_SECRET_ACCESS_KEY"]
    data["OCP_CONSOLE_URL"] = config_data["TEST_CLUSTERS"][test_cluster]["OCP_CONSOLE_URL"]
    data["ODH_DASHBOARD_URL"] = config_data["TEST_CLUSTERS"][test_cluster]["ODH_DASHBOARD_URL"]
    data["TEST_USER"]["AUTH_TYPE"] = config_data["TEST_CLUSTERS"][test_cluster]["TEST_USER"]["AUTH_TYPE"] 
    data["TEST_USER"]["USERNAME"] = config_data["TEST_CLUSTERS"][test_cluster]["TEST_USER"]["USERNAME"]
    data["TEST_USER"]["PASSWORD"] = config_data["TEST_CLUSTERS"][test_cluster]["TEST_USER"]["PASSWORD"]
    data["OCP_ADMIN_USER"]["AUTH_TYPE"] = config_data["TEST_CLUSTERS"][test_cluster]["OCP_ADMIN_USER"]["AUTH_TYPE"]
    data["OCP_ADMIN_USER"]["USERNAME"] = config_data["TEST_CLUSTERS"][test_cluster]["OCP_ADMIN_USER"]["USERNAME"]
    data["OCP_ADMIN_USER"]["PASSWORD"] = config_data["TEST_CLUSTERS"][test_cluster]["OCP_ADMIN_USER"]["PASSWORD"]

    with open(config_file, 'w') as yaml_file:
        yaml_file.write( yaml.dump(data, default_flow_style=False, sort_keys=False))

def main():
    """main function"""

    args = parse_args()

    clone_config_repo(git_repo = args.git_repo,
                      git_branch = args.git_repo_branch,
                      repo_dir = args.repo_dir,
                      git_username = args.git_username,
                      git_password = args.git_password)

    config_file = args.repo_dir + "/test-variables.yml"
    config_data = getConfigData(config_file)
    
    # Generate test config file
    generate_test_config_file(args.config_template, config_data, args.test_cluster)


if __name__ == '__main__':
    main()
