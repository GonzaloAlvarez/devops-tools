# Python XEN Client

import logging, yaml, pprint, XenAPI

class XenClient:
    def __init__(self, conffile):
        stream = open(conffile, "r")
        self.config = yaml.load(stream)
        url = self.config["xen_url"]
        user = self.config["xen_user"]
        password = self.config["xen_pass"]
        self.session = XenAPI.Session(url)
        self.session.xenapi.login_with_password(user, password)

    def getVMList(self, filter="regular"):
        all_vms = self.session.xenapi.VM.get_all_records()
        vms = []
        for vm in all_vms:
            if filter == "control" and all_vms[vm]["is_control_domain"]:
                vms.append(all_vms[vm])
                break # Only one control VM (Dom0)
            if filter == "templates" and all_vms[vm]["is_a_template"]:
                vms.append(all_vms[vm])
                continue
            if all_vms[vm]["is_a_template"]:
                continue
            if filter == "regular":
                vms.append(all_vms[vm])
                continue
            if filter == "running" and all_vms[vm]["power_state"] == "Running":
                vms.append(all_vms[vm])
                continue
            if filter == "halted" and all_vms[vm]["power_state"] == "Halted":
                vms.append(all_vms[vm])
                continue
        return vms


    def close(self):
        self.session.xenapi.logout()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    xenClient = XenClient('config.yaml')
    vms = xenClient.getVMList("running")
    for vm in vms:
        pprint.pprint(vm)
    xenClient.close()
