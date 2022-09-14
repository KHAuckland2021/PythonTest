import os
import platform
import time
import psutil
import win32service
import win32serviceutil
import zipfile
import logging
import subprocess
import jsonpickle
from psutil._pswindows import WindowsService
from win32api import GetFileVersionInfo, LOWORD, HIWORD

logging.basicConfig(
    filename='.\\deployment-agent.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-6s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class ServiceInformation:
    """
    Holds information about a given windows service
    """

    def __init__(self, windows_service: WindowsService):
        self.machine = platform.node()
        self.service_bin_path = windows_service.binpath().split(' ')[0].strip('"')
        self.service_name = windows_service.display_name()
        self.status = windows_service.status()
        self.version = self.get_version_number(self.service_bin_path)

    @staticmethod
    def get_version_number(service_file_name):
        try:
            info = GetFileVersionInfo(service_file_name, "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            return f'{HIWORD(ms)}.{LOWORD(ms)}.{HIWORD(ls)}.{LOWORD(ls)}'
        except Exception as ex:
            print(str(ex))
            return "Unknown version"


class DeploymentAgent:
    """
    This class implements the agent part of the software deployment framework
    """

    def __init__(self):
        self.service_install_batch = "installService.bat"
        logging.info('Create DeploymentAgent')

    """
    Given a service (display) name this function gathers information about the service
    which will be stored then in an object of type ServiceInformation
    """

    @staticmethod
    def get_service_info(service_name):
        logging.info(f'get_service_info: {service_name}')
        try:
            windows_service = psutil.win_service_get(service_name)
            service_information = ServiceInformation(windows_service)
            logging.info(jsonpickle.encode(service_information))
            return service_information
        except Exception as ex:
            logging.error(f'{service_name}: {str(ex)}')

    def install_service(self, zip_package, destination_folder):
        logging.info(f'install_service: destination_folder: {destination_folder}')
        try:
            if zip_package:
                logging.info(f'install_service: zip_package: {zip_package}')
                with zipfile.ZipFile(zip_package, 'r') as zip_ref:
                    zip_ref.extractall(destination_folder)
            # Call the service installation batch file
            service_batch_file = os.path.join(destination_folder, self.service_install_batch)
            p = subprocess.Popen(service_batch_file, shell=True, stdout=subprocess.PIPE, cwd=destination_folder)
            p.communicate()
            logging.info(f'install_service returns: {p.returncode}')

        except Exception as ex:
            logging.error(f'install_service {zip_package} failed: {str(ex)}')

    @staticmethod
    def start_service(service_name):
        logging.info(f'start_service: {service_name}')
        try:
            win32serviceutil.StartService(service_name)
            service_status = win32serviceutil.QueryServiceStatus(service_name)[1]
            if service_status == win32service.SERVICE_START_PENDING:
                time.sleep(5)
        except Exception as ex:
            logging.error(f'{service_name}: {str(ex)}')

    @staticmethod
    def stop_service(service_name):
        logging.info(f'stop_service: {service_name}')
        try:
            win32serviceutil.StopService(service_name)
            service_status = win32serviceutil.QueryServiceStatus(service_name)[1]
            if service_status == win32service.SERVICE_STOP_PENDING:
                time.sleep(5)
        except Exception as ex:
            logging.error(f'{service_name}: {str(ex)}')


# -------------------------------------------------------------------------------------------
if __name__ == '__main__':
    test_service_path = "/path/to/the/service"
    test_service_name = "NameOfTheService"

    deployment_agent = DeploymentAgent()

    service_info = deployment_agent.get_service_info(test_service_name)

    deployment_agent.install_service("", test_service_path)
    deployment_agent.start_service(test_service_name)
    service_info = deployment_agent.get_service_info(test_service_name)

    deployment_agent.stop_service(test_service_name)
    service_info = deployment_agent.get_service_info(test_service_name)
