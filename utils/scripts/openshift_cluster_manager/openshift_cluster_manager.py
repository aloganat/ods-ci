def setup_osd_cluster(self):
        """Sets up the osd cluster"""

        if not bool(self.skip_cluster_creation):
            if not self.is_osd_cluster_exists():
                self.osd_cluster_create()
                self.wait_for_osd_cluster_to_be_ready()
        else:
            print ("cluster create step got skipped!!")
        if not bool(self.skip_rhods_installation):
            if not self.is_addon_installed():
                self.install_rhods()
                self.wait_for_addon_installation_to_complete()
        else:
            print ("managed-ods addon installation got skipped!!")
        if bool(self.create_cluster_admin_user):
            self.create_idp()
            self.add_user_to_group()

        if not bool(self.skip_cluster_creation) or not bool(self.skip_rhods_installation) or bool(self.create_cluster_admin_user):
            # Waiting 5 minutes to ensure all the cluster services are
            # up even after cluster is in ready state

            time.sleep(300)
        self.get_osd_cluster_info()

    def login(self):
        """ Login to OCM using ocm cli"""

        cmd = "ocm login --token=\"{}\" ".format(self.login_token)
        if self.testing_platform == "stage":
            cmd += "--url=staging"

        ret = execute_command(cmd)
        if ret is None:
            print("Failed to login to aws openshift platform using token")
            sys.exit(1)


def parse_args():
    """Parse CLI arguments"""

    ocm_cli_binary_url = ("https://github.com/openshift-online/ocm-cli/"
                          "releases/download/v0.1.55/ocm-linux-amd64")
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Script to generate test config file')
    parser.add_argument("-i", "--awsaccountid",
                        help="aws account id",
                        action="store", dest="aws_account_id",
                        required=True)
    parser.add_argument("-a", "--awsaccesskeyid",
                        help="aws access key id",
                        action="store", dest="aws_access_key_id",
                        required=True)
    parser.add_argument("-k", "--awssecretaccesskey",
                        help="aws secret access key",
                        action="store", dest="aws_secret_access_key",
                        required=True)
    parser.add_argument("-l", "--logintoken",
                        help="openshift token for login",
                        action="store", dest="login_token",
                        required=True)
    parser.add_argument("-p", "--testingplatform",
                        help="testing platform. 'prod' or 'stage'",
                        action="store", dest="testing_platform",
                        default="stage")
    parser.add_argument("-e", "--clustername",
                        help="osd cluster name",
                        action="store", dest="cluster_name",
                        default="osd-qe-1")
    parser.add_argument("-r", "--awsregion",
                        help="aws region",
                        action="store", dest="aws_region",
                        default="us-east-1")
    parser.add_argument("-t", "--awsinstancetype",
                        help="aws instance type",
                        action="store", dest="aws_instance_type",
                        default="m5.2xlarge")
    parser.add_argument("-c", "--numcomputenodes",
                        help="Number of compute nodes",
                        action="store", dest="num_compute_nodes",
                        default="3")
    parser.add_argument("-s", "--skip-cluster-creation",
                        help="skip osd cluster creation",
                        action="store_true", dest="skip_cluster_creation")
    parser.add_argument("-x", "--skip-rhods-installation",
                        help="skip rhods installation",
                        action="store_true", dest="skip_rhods_installation")
    parser.add_argument("-m", "--create-cluster-admin-user",
                        help="create cluster admin user for login",
                        action="store_true", dest="create_cluster_admin_user")
    parser.add_argument("-q", "--create-ldap-idp",
                        help="create ldap idp and add users to rhods groups",
                        action="store_true", dest="create_ldap_idp")
    parser.add_argument("-d", "--delete-ldap-idp",
                        help="delete ldap idp",
                        action="store_true", dest="delete_ldap_idp")
    parser.add_argument("-o", "--ocmclibinaryurl",
                        help="ocm cli binary url",
                        action="store", dest="ocm_cli_binary_url",
                        default=ocm_cli_binary_url)

    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()
    ocm_obj = OpenshiftClusterManager(args)
    ocm_obj.ocm_cli_install()
    ocm_obj.login()
    ocm_obj.setup_osd_cluster()

    if bool(args.create_ldap_idp):
        ocm_obj.create_idp(type="ldap")
        ocm_obj.add_users_to_rhods_group()
        time.sleep(120)

    if bool(args.delete_ldap_idp):
        print ("delete")
        ocm_obj.delete_idp("ldap-provider-qe")
        time.sleep(120)
