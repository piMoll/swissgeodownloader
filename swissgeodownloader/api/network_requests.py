import json

from qgis.PyQt.QtCore import (
    QByteArray,
    QEventLoop,
    QUrl,
    QUrlQuery
)
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.core import QgsBlockingNetworkRequest, QgsFileDownloader

from swissgeodownloader.api.apiCallerTask import ApiCallerTask
from swissgeodownloader.utils.utilities import tr

trc = "ApiInterface"


def fetch(
        task: ApiCallerTask,
        url: QUrl | str,
        params=None,
        header=None,
        method="get",
        decoder="json",
) -> dict | QByteArray:
    """Perform a blocking network request without the help of the
    QgsStacController. This is necessary because the controller does not
    parse all available item/asset properties of the response."""
    
    request = QNetworkRequest()
    # Prepare url
    callUrl = createUrl(url, params)
    request.setUrl(callUrl)
    
    if header:
        request.setHeader(*tuple(header))
    
    task.log(tr("Start request {}", trc).format(callUrl))
    # Start request
    http = QgsBlockingNetworkRequest()
    if method == "get":
        http.get(request, forceRefresh=True)
    elif method == "head":
        http.head(request, forceRefresh=True)
    
    # Check if request was successful
    r = http.reply()
    try:
        assert r.error() == QNetworkReply.NetworkError.NoError, r.error()
    except AssertionError:
        # Service is not reachable
        task.exception = tr(
            "{} not reachable or no internet connection", trc).format(callUrl)
        # Service returned an error
        if r.content():
            try:
                errorResp = json.loads(str(r.content(), "utf-8"))
            except json.JSONDecodeError as e:
                task.exception = str(e)
                raise e
            if "code" and "description" in errorResp:
                task.exception = (
                        tr("{} returns error", trc).format(callUrl)
                        + f": {errorResp['code']} - {errorResp['description']}"
                )
        return False
    
    # Process response
    if method == "get":
        if decoder == "json":
            try:
                content = str(r.content(), "utf-8")
                if content:
                    return json.loads(content)
                else:
                    raise Exception('Empty response')
            except json.JSONDecodeError as e:
                task.exception = str(e)
                raise Exception(task.exception)
        else:  # decoder string
            return r.content()
    elif method == "head":
        return r
    else:
        raise Exception(f"Method {method} not supported")

    
def fetchFile(task: ApiCallerTask, url: QUrl | str, filename: str,
              filePath: str, part: float, params: dict | None = None):
    # Prepare url
    callUrl = QUrl(url)
    if params:
        queryParams = QUrlQuery()
        for key, value in params.items():
            queryParams.addQueryItem(key, str(value))
        callUrl.setQuery(queryParams)
    
    task.log(tr('Start download of {}', trc).format(callUrl.toString()))
    fileFetcher = QgsFileDownloader(callUrl, filePath)
    
    def onError():
        task.exception = tr('Error when downloading {}', trc).format(filename)
        return False
    
    def onProgress(bytesReceived, bytesTotal):
        if task.isCanceled():
            task.exception = tr('Download of {} was canceled', trc).format(
                    filename)
            fileFetcher.cancelDownload()
        else:
            partProgress = 0
            if bytesTotal > 0:
                partProgress = (part / 100) * (bytesReceived / bytesTotal)
            task.setProgress(task.progress() + partProgress)
    
    # Run file download in separate event loop
    eventLoop = QEventLoop()
    fileFetcher.downloadError.connect(onError)
    fileFetcher.downloadCanceled.connect(eventLoop.quit)
    fileFetcher.downloadCompleted.connect(eventLoop.quit)
    fileFetcher.downloadProgress.connect(onProgress)
    eventLoop.exec(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
    fileFetcher.downloadCompleted.disconnect(eventLoop.quit)


def createUrl(baseUrl: QUrl | str, urlParams: dict | None):
    url = QUrl(baseUrl)
    if urlParams:
        queryParams = QUrlQuery()
        for key, value in urlParams.items():
            if value is None or value == "" or value == []:
                continue
            if isinstance(value, list):
                param = ",".join([str(v) for v in value])
            else:
                param = str(value)
            queryParams.addQueryItem(key, param)
        url.setQuery(queryParams)
    return url
