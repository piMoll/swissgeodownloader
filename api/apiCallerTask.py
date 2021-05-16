from qgis.core import QgsTask, QgsMessageLog, Qgis
from .api_datageoadmin import (getFileList, downloadFiles)

MESSAGE_CATEGORY = 'Swiss Geo Downloader'


class ApiCallerTask(QgsTask):
    def __init__(self, apiRef, func, callParams):
        # TODO
        description = func
        super().__init__(description, QgsTask.CanCancel)
        self.apiRef = apiRef
        self.func = func
        self.callParams = callParams
        self.output = None
        self.exception = None
    
    def run(self):
        """Here the time consuming requests are started. This method MUST
         return True or False. Raising exceptions will crash QGIS, so we
         handle them internally and raise them in self.finished"""
        
        if self.func == 'getDatasetList':
            self.output = self.apiRef.getDatasetList(self)
        
        elif self.func == 'getFileList':
            self.output = getFileList(self,
                                      self.callParams['dataset'],
                                      self.callParams['bbox'],
                                      self.callParams['timestamp'],
                                      self.callParams['options'])
        
        elif self.func == 'downloadFiles':
            self.output = downloadFiles(self,
                                        self.callParams['fileList'],
                                        self.callParams['folder'])
        return True
    
    def finished(self, result):
        """This function is automatically called when the task has
        completed (successfully or not)"""
        if result:
            msg = 'request completed'
            if self.func == 'getDatasetList':
                msg = 'available datasets received'
            elif self.func == 'getFileList':
                msg = 'file list received'
            elif self.func == 'downloadFiles':
                msg = 'files downloaded'
            QgsMessageLog.logMessage(msg, MESSAGE_CATEGORY, Qgis.Success)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('an unknown error occured',
                    MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage(
                    f'Exception: {self.exception}',
                    MESSAGE_CATEGORY, Qgis.Critical)
                # raise self.exception

    def cancel(self):
        super().cancel()
