import base64
import copy
import datetime
import logging
import multiprocessing
import os
import platform
import queue
import random
import signal
import sys
import threading
import time
import traceback
import urllib
import uuid
from pathlib import Path

from flask import Flask, request, send_from_directory
from flask_cors import CORS
from AWSState import CloudState, CloudLog
# force multiprocessing to do fork properly: https://pythonspeed.com/articles/python-multiprocessing/
from multiprocessing import set_start_method, Process
from perplexity.state import LoadException
from perplexity.user_interface import load_ui, command_save
from perplexity.user_state import GetStateDirectoryName
from perplexity.world_registry import ui_from_world_name, world_information

set_start_method("spawn", True)
app = Flask(__name__)
CORS(app)


# *****************
#
# ** Webserver **
# A thread is used for each request.
# It finds the worker the user is pinned to or picks a new one and sends it the request
#       A worker gets optimized to a particular user, if the user comes back, it is primed and cached for them
# It blocks (with timeout) waiting for its request to be processed by the worker
#
# In the webserver process is a thread that processes all responses from all workers
#       This is because we had no way to send workers a new queue that the request thread could wait on
#
# ** Worker **
# The Worker receives the message and processes it
#       When request comes in, we load state to make sure it hasn't been changed from what we last processed
#           If it hasn't, then we go forward, if it has, we reload
# It sends the response on a global queue that is shared by all workers
#
# Architecture assumes that all requests are in the same process and also that all processes can share the global queue
#
# *****************
@app.before_request
def StartWorkers():
    # The following line will remove this handler, making it
    # only run on the first request
    # This needs to be done so that the process creation can complete
    # and then create the child processes when the first request happens
    app.before_request_funcs[None].remove(StartWorkers)

    global multiprocessManager
    global workerDataMutex
    global workerIDs
    global responseQueue
    global waitingThreads
    global waitingThreadsMutex
    global response_thread

    # Create globals
    multiprocessManager = multiprocessing.Manager()
    responseQueue = multiprocessManager.Queue()
    waitingThreadsMutex = threading.Lock()
    waitingThreads = dict()

    # Start the response thread
    response_thread = threading.Thread(target=ResponseThread)
    response_thread.start()

    processorCount = os.cpu_count()
    processorCount = None
    if processorCount is None:
        processorCount = 2
    log.critical(f"Starting {processorCount} workers")

    with workerDataMutex:
        for _ in range(0, processorCount):
            workerData = StartWorker()
            workerIDs[workerData["ProcessID"]] = workerData


@app.route('/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


# Main REST entry point
@app.route("/", methods=['GET', 'POST'])
def root_reply():
    try:
        # No 'From' means just a quick health check
        if 'From' not in request.values:
            return "healthy"

        # Build a workitem for the workers
        # Use values so get and post both work for debugging
        sender = request.values['From']
        msg = request.values['Body']
        interface = "website" if 'Interface' not in request.values else request.values['Interface']
        game = request.values['Game'] if "Game" in request.values else None
        requestID = str(uuid.uuid1())
        workItem = {"ID": requestID,
                    "Sender": sender,
                    "Body": msg,
                    "Game": game,
                    "Interface": interface}

        # Queue the request up to a worker and wait for the response
        response = SendMessageGetResponse(workItem)

        log.info(f"Respond with: ID: {requestID}, From:{sender}, Msg:{msg}, Response:{response['Reply']}")
        return response['Reply']

    except:
        log.critical("Unexpected error: {}".format(traceback.format_exc()))
        return "Problem -> Sorry! We are having technical difficulties. Try again later"


# Remotely ask to exit
@app.route("/sloppyexit", methods=['GET', 'POST'])
def SloppyExit():
    global workerDataMutex
    global workerIDs

    with workerDataMutex:
        for workerData in workerIDs.values():
            workItem = {"quit": True}
            workerData["WorkQueue"].put(workItem, block=True, timeout=30)
            log.critical(f"QUEUED Exit for {workerData['ProcessID']}")

    time.sleep(5)
    log.info("killing process.")
    sig = getattr(signal, "SIGKILL", signal.SIGTERM)
    os.kill(os.getpid(), sig)


@app.route("/versionsettest", methods=['GET', 'POST'])
def VersionSetTest():
    global workerDataMutex
    global workerIDs

    try:
        with workerDataMutex:
            for workerData in workerIDs.values():
                workItem = {"SetVersion": True}
                workerData["WorkQueue"].put(workItem, block=True, timeout=30)
                log.critical(f"QUEUED version change for {workerData['ProcessID']}")

        return "set version initiated"

    except:
        log.critical("Unexpected error: {}".format(traceback.format_exc()))
        return "Sorry! We are having technical difficulties. Try again later"


# Responses to requests are all sent on a single shared queue so that we can
# have a single listening thread that demultiplexes them and unblocks the right thread
# Would have preferred to have a queue created by each request and sent to the worker
# along with the workitem but couldn't marshall a queue across process
def ResponseThread():
    global waitingThreadsMutex
    global waitingThreads
    global workerDataMutex
    global workerIDs
    global responseQueue

    while True:
        try:
            # Pull the response from the queue and notify
            # the appropriate thread to wake up
            # Hand it the response and remove the thread from the dict
            response = responseQueue.get(True, 60)
            with waitingThreadsMutex:
                if isinstance(response, dict):
                    if "Protocol" in response:
                        # This is a response to some protocol interaction not a
                        # real user request
                        if response["Protocol"] == "requestedExitComplete" or response["Protocol"] == "workerExit":
                            with workerDataMutex:
                                workerIDs.pop(response["WorkerID"])
                                log.critical(f"Worker {response['WorkerID']} exited cleanly")

                        if response["Protocol"] == "workerExit":
                            with workerDataMutex:
                                # Create and register a replacement worker
                                workerData = StartWorker()
                                workerIDs[workerData["ProcessID"]] = workerData

                    if "ID" in response:
                        # Update the stats we track for the worker since we got a valid response
                        with workerDataMutex:
                            workerID = response["WorkerID"]
                            if workerID in workerIDs:
                                worker = workerIDs[workerID]
                                worker["PendingMessages"] -= 1
                                if worker["PendingMessages"] > 0:
                                    # There are more messages in the queue, the worker will end up pulling the next one
                                    # out now, so record now as the "sent time" for the next message
                                    worker["PendingMessageSentTime"] = datetime.datetime.now()
                                else:
                                    worker["PendingMessageSentTime"] = None

                        # Thread may have already exited
                        if response["ID"] in waitingThreads:
                            threadInfo = waitingThreads.pop(response["ID"])
                            threadInfo["Reply"] = response["Reply"]
                            threadInfo["Event"].set()

                else:
                    raise ValueError(f'unexpected value from worker: {response}')

        except queue.Empty:
            # Timed out waiting for message
            log.info(
                f"Response thread timed out waiting for message, retrying...")

        except Exception as err:
            log.critical(f"Worker {response['WorkerID']} had error {str(err)}. Killing process")

            # Kill the whole process and all workers before exiting
            SafelyKillProcess()


def StartWorker():
    global multiprocessManager
    global workerDataMutex
    global workerIDs
    global responseQueue

    workQueue = multiprocessManager.Queue(maxsize=maxWorkerQueueSize)
    remoteArgsTuple = (workQueue, responseQueue)
    p = Process(target=DoWork, args=remoteArgsTuple)
    p.start()
    log.critical(f"Started new worker process {p.pid}")
    return {"ProcessID": p.pid,
            "Process": p,
            "PinnedUser": None,
            "WorkQueue": workQueue,
            "LastPinnedUserMessage": datetime.datetime.now(),
            "PendingMessages": 0,
            "PendingMessageSentTime": None}


# Finds an appropriate worker, sends the workitem,
# and returns the response or throws
def SendMessageGetResponse(workItem):
    global workerDataMutex
    global multiprocessManager
    global waitingThreadsMutex
    global waitingThreads

    log.info(f"SendMessageGetResponse for workitem: {workItem}")

    # Get the worker to use
    workerData = FindWorkerForUser(workItem["Sender"])
    workItem["WorkerID"] = workerData["ProcessID"]

    # Let the ResponseThread know that a request has been queued up
    # So it can unblock us when the response comes
    waitEvent = threading.Event()
    requestObject = {"Event": waitEvent}
    requestID = workItem["ID"]
    with waitingThreadsMutex:
        waitingThreads[requestID] = requestObject

    # Now send the work to the worker's work queue
    with workerDataMutex:
        workerData["WorkQueue"].put(workItem, block=False)

    log.info(f"QUEUED in worker {workerData['ProcessID']}: ID:{requestID}, From:{workItem['Sender']}, Msg:{workItem['Body']}")

    # We get notified when a worker has processed this
    # If it was successful, the request object has had its "Reply" key filled it
    if not waitEvent.wait(workerProcessMessageTimeout):
        # We timed out. Note that the worker will continue processing the message, however.
        # If it times out, the worker crashed or is really slow.
        log.critical(f"Timed out waiting for worker: {requestID}")
        requestObject["Reply"] = "Could you try a different wording? That will take me a while to think through."

    return requestObject


# If the user is assigned a worker, use that one.
# Otherwise, see if there is an unassigned or timed-out worker and assign and use that one
# If none is unassigned, use the least queued in a way that will always pick the same
#       ones if you can so (mostly) only one gets its caches thrashed
def FindWorkerForUser(userID):
    global workerDataMutex
    global workerIDs

    shortestQueue = sys.maxsize
    shortestQueueWorker = None
    with workerDataMutex:
        # Use this opportunity to restart hung workers
        CheckWorkersHealth()

        unassignedWorker = None
        for workerData in workerIDs.values():
            if workerData["PinnedUser"] == userID:
                # Found the worker assigned to this user
                # Update their last used time
                return UseWorkerForMessage(workerData, userID)

            elif workerData["PinnedUser"] is None:
                # Nobody assigned, we could just use it
                unassignedWorker = workerData

            elif (datetime.datetime.now() - workerData["LastPinnedUserMessage"]).total_seconds() > workerAssignmentTimeoutSeconds:
                # Person timed out, we could use it
                unassignedWorker = workerData

            else:
                # This one is busy, but remember it if it is the least busy
                pendingMessages = workerData["PendingMessages"]
                if pendingMessages < shortestQueue:
                    shortestQueueWorker = workerData
                    shortestQueue = pendingMessages

        # If an assignment wasn't found, then use an unusedWorker if there is one
        # Otherwise, use the shortestQueueWorker but don't assign the worker to this person.
        #               This way, the user will keep trying to get their own worker over time
        #               and they will always pick the same worker (if it isn't busy) so it won't mess up the cache
        #               for everyone
        if unassignedWorker is not None:
            return UseWorkerForMessage(unassignedWorker, userID)
        else:
            # Don't assign the worker to this person
            return UseWorkerForMessage(shortestQueueWorker, None)


# Pass user = None to use, but not assign, this worker
def UseWorkerForMessage(workerData, user):
    if user is not None:
        workerData["PinnedUser"] = user
        workerData["LastPinnedUserMessage"] = datetime.datetime.now()

    # Regardless of who is sending, we need to track total messages in transit
    workerData["PendingMessages"] += 1
    if workerData["PendingMessageSentTime"] is None:
        workerData["PendingMessageSentTime"] = datetime.datetime.now()

    return workerData


def CheckWorkersHealth():
    global workerDataMutex
    global workerIDs

    newWorkerIDs = {}
    with workerDataMutex:
        for workerData in workerIDs.values():
            newWorker = HandleWorkerFail(workerData)
            if newWorker is None:
                newWorkerIDs[workerData["ProcessID"]] = workerData
            else:
                newWorkerIDs[newWorker["ProcessID"]] = newWorker

        workerIDs = newWorkerIDs


# workerData["Messages"] tracks which messages are currently in the queue OR being processed
# if the "next" message has been there for > X seconds, assume the worker died or hung
# kill it, and restart
def HandleWorkerFail(workerData):
    global workerDataMutex
    global workerHungSeconds
    global lastCrash
    global crashCount
    global lastCrashSecondsWindow

    with workerDataMutex:
        if workerData["PendingMessageSentTime"] is not None:
            # We have sent a message that we haven't received an answer for yet
            secondsSinceMessageReceived = (datetime.datetime.now() - workerData["PendingMessageSentTime"]).total_seconds()
            if secondsSinceMessageReceived > workerHungSeconds:
                # Assume the worker is hung, try to kill it
                log.critical(f"Worker ID: {workerData['ProcessID']} is assumed hung since message has been waiting {secondsSinceMessageReceived} seconds to process")
                sig = getattr(signal, "SIGKILL", signal.SIGTERM)
                try:
                    os.kill(workerData["ProcessID"], sig)
                except:
                    pass

                timeSinceLastCrash = (datetime.datetime.now() - lastCrash).total_seconds()
                lastCrash = datetime.datetime.now()
                if timeSinceLastCrash > lastCrashSecondsWindow:
                    # We'll try restarting as long as the last crash was a while ago
                    # to avoid looping when things are really bad
                    log.critical(f"Restarting worker since time in seconds since last crash was: {timeSinceLastCrash}")
                    crashCount = 1
                    return StartWorker()
                else:
                    crashCount += 1
                    if crashCount <= maxCrashesInWindow:
                        # We'll try a few times if we are in the window
                        log.critical(f"Restarting worker since time in seconds since last crash was in window ({timeSinceLastCrash}) but only {crashCount} crashes")
                        return StartWorker()
                    else:
                        log.critical(f'{crashCount} crashes, in too short of a window, exiting')
                        SafelyKillProcess()
        else:
            log.info(f"Worker ID: {workerData['ProcessID']} has no messages pending.")

        # No new workers created
        return None


def SafelyKillProcess():
    global workerDataMutex

    log.critical("SafelyKillProcess: Kill outstanding workers")

    # Kill any outstanding workers
    sig = getattr(signal, "SIGKILL", signal.SIGTERM)
    with workerDataMutex:
        for workerData in workerIDs.values():
            os.kill(workerData["ProcessID"], sig)

    # Now kill the process
    log.critical("Killing process: Unexpected error in ResponseThread: {}".format(traceback.format_exc()))
    os.kill(os.getpid(), sig)


def ReplyWithMessage(responseQueue, userID, message):
    global currentWorkItem
    if currentWorkItem is not None:
        OutputMessage("", userID, "", message)
        responseQueue.put(currentWorkItem)


def ReplyWithMessageAndExitWorker(responseQueue, userID, message, processID):
    global currentWorkItem
    if currentWorkItem is not None:
        OutputMessage("", userID, "", message)
    else:
        currentWorkItem = {}

    currentWorkItem["Protocol"] = "workerExit"
    currentWorkItem["WorkerID"] = processID
    responseQueue.put(currentWorkItem)


def DoWork(workQueue, responseQueue):
    global startGameDefault
    # Make this global so we can collect text from all sources
    global currentWorkItem
    processID = os.getpid()
    nodeName = platform.node()
    unencodedUserID = ""
    userID = None
    cachedUser = None

    log.info(f"Starting worker {processID}...")
    try:
        state = CloudState(project="Perplexity", bucketName="perplexityusers")
        log.info("Connected to cloud state...")

        # funcIn = lambda value: InputMessage(userID, "", value)
        # funcOut = lambda value: OutputMessage(unencodedUserID, userID, "", value)
        # funcDebug = lambda value: DebugMessage(userID, value)
        # adventureUI = TextUI("default", funcOut, funcIn, funcDebug)
        # adventureUI.planner.showImages = True
        # adventureUI.planner.userState["LastMessageTime"] = None

        cached_ui = None
        while True:
            log.info(f"Worker {processID} is waiting for messages with cached user state for {cachedUser}...")

            try:
                # Get the next item from the queue
                currentWorkItem = None
                newWorkItem = workQueue.get(block=True, timeout=workQueueTimeoutSeconds)
                if "quit" in newWorkItem:
                    log.info(f"Exit requested. Exiting worker {processID}")
                    responseQueue.put({"Protocol": "requestedExitComplete", "WorkerID": processID})
                    break

                # elif "SetVersion" in newWorkItem:
                #     adventureUI.planner.gameBuild += 1
                #     log.info(f"Worker {processID} set engine version to {adventureUI.planner.gameBuild}...")
                #     log.info(f"Worker {processID} released cached user {cachedUser}...")
                #     cachedUser = None
                #     responseQueue.put({})
                #     continue

                # Create a reply entry to collect all replies and then
                # Set the global workitem to actually collect the responses
                newWorkItem["Reply"] = ""
                currentWorkItem = newWorkItem

                # Don't crash if we can't parse the request, just continue
                try:
                    # Base64 encode so we aren't exposed to attacks or bugs
                    unencodedUserID = currentWorkItem["Sender"]
                    userID = base64.urlsafe_b64encode(currentWorkItem["Sender"].encode('utf-8')).decode('utf-8')
                    message = currentWorkItem["Body"]
                    interface = currentWorkItem["Interface"] if "Interface" in currentWorkItem else "unknown"
                    audioInput = False if "-text" in interface.lower() else True
                    # parts = message.strip().lower().split(" ")
                    # if len(parts) == 2 and parts[0] == "play" and adventureUI.ValidGame(parts[1]):
                    #     startGame = adventureUI.ValidGame(parts[1])
                    # else:
                    #     startGame = currentWorkItem["Game"] if (
                    #                 "Game" in currentWorkItem and currentWorkItem["Game"] is not None) else startGameDefault
                    startGame = currentWorkItem["Game"] if (
                                "Game" in currentWorkItem and currentWorkItem["Game"] is not None) else startGameDefault
                    if world_information(startGame) is None:
                        ReplyWithMessage(responseQueue, userID, "Problem -> Perplexity was had an issue. Send again if you want a reply.")
                        continue

                except:
                    ReplyWithMessage(responseQueue, userID, "Problem -> Perplexity was had an issue. Send again if you want a reply.")
                    continue

                # Do the work
                log.info(f"Worker {processID} processing: ID: {currentWorkItem['ID']}, Interface:{interface}, From:{userID}, Game:{startGame}, Msg:{message}")
                perfDict = {'LoadDataTime': None, 'LoadGameTime': None, 'LastInterpretationTime': None}

                # Load user data
                log.info(f"Loading user data for: {userID}")
                loadTimeStart = time.perf_counter()
                userDirectory = GetStateDirectoryName(userID)
                if not os.path.exists(userDirectory):
                    os.makedirs(userDirectory)
                rawStatePath = os.path.join(userDirectory, "state.p8y")
                dataInfo = state.LoadState(userID, rawStatePath)
                perfDict["LoadDataTime"] = time.perf_counter() - loadTimeStart

                # Start the Log
                ClearLog(userID)
                backupLogID = dataInfo["Key"] + "-" + datetime.datetime.now().strftime("%H%M%S%z%f") + ".backup"
                LogText(userID, f"\n--------------- {datetime.datetime.now()} - {nodeName}@{processID}: Interface:{interface}, AfterInteractionData: {backupLogID}\nUSER: {message}\n")

                # Run the actual game iteration
                if cachedUser == userID and dataInfo["Generation"] != cachedUserDataGeneration:
                    # If the data got updated since we last loaded, don't use it
                    log.info(f"Stored generation: {dataInfo['Generation']} does not match last user generation: {cachedUserDataGeneration}")
                    cachedUser = None

                cached_ui = RunGameIteration(cachedUser, perfDict, rawStatePath, dataInfo, startGame, state, cached_ui, userID, unencodedUserID, message, audioInput)
                # log.info(f"Finished: {userID} - {cached_ui.answer}")
                # perfDict["LastInterpretationTime"] = adventureUI.planner.lastSemanticResult['LastInterpretationTime'] if adventureUI.planner.lastSemanticResult is not None and "LastInterpretationTime" in adventureUI.planner.lastSemanticResult else None
                # LogText(userID, f"\n--------------- LoadData: {perfDict['LoadDataTime']}, LoadGame: {perfDict['LoadGameTime']}, Interpretation: {perfDict['LastInterpretationTime']}\n")

                # Reply with the finished work before saving just to save time
                log.info(f"Worker {processID} responding: ID: {currentWorkItem['ID']}, Response:{currentWorkItem['Reply']}")

                # Don't record any system messages for the user from here on out
                responseQueue.put(currentWorkItem)
                currentWorkItem = None

                # Finally actually save all the work off
                SaveDataAfterTurn(backupLogID, rawStatePath, cached_ui, state, dataInfo, userID, unencodedUserID, message)

                # Save the cached user after saving because the generation stored in dataInfo will be new
                cachedUser = userID
                cachedUserDataGeneration = dataInfo["Generation"]

            except queue.Empty:
                # Timed out waiting for messages
                # Would be a good time to do housekeeping but none to do at the moment
                # so just try again
                log.info(f"Worker {processID} timed out waiting for message, trying again")

    except KeyboardInterrupt:
        ReplyWithMessage(responseQueue, userID, "Problem -> Perplexity was halted.")

    except:
        log.critical(f"Worker {processID} crashing: {traceback.format_exc()}")
        ReplyWithMessageAndExitWorker(responseQueue, userID, "Problem -> Perplexity was had an issue. Send again if you want a reply.", processID)


def SaveDataAfterTurn(backupLogID, rawStatePath, ui, state, dataInfo, userID, unencodedUserID, message):
    dataInfoBackup = copy.deepcopy(dataInfo)
    dataInfoBackup["Key"] = backupLogID
    dataInfoBackup["rawStatePath"] = rawStatePath

    # Save the user's game state locally so that it is cached if the
    # same user comes through again
    command_save(ui, rawStatePath)

    # Actually save the user state in the cloud so it can be reloaded
    state.Save(dataInfo, rawStatePath)

    # Now save the logs, this should never fail from a conflict, it just keeps retrying
    if unencodedUserID != "healthcheck":
        state.CreateOrAppendLog(userID + "Log", LogFileName(userID))
        log.info("Saved state for user: {}".format(userID))

    # Save out a copy of the state after interaction so we can debug later
    if dataInfoBackup is not None:
        log.info(f"Worker {os.getpid()} saving backup: {dataInfoBackup['Key']}")
        state.Save(dataInfoBackup, dataInfoBackup["rawStatePath"], True)


# Leaves the last users state loaded in memory.
# If the user is the same, just does a quick check to make sure no other process has
# loaded it and moves on
def RunGameIteration(cachedUser, perfDict, rawStatePath, dataInfo, startGame, state, ui, userID, unencodedUserID, message, audioInput):
    funcOut = lambda value: OutputMessage(unencodedUserID, userID, "", value)
    funcDebug = lambda value: DebugMessage(userID, value)

    isNewUser = dataInfo["NewUser"]
    perfDict["LoadGameTime"] = None

    # Get the state loaded for an existing user
    if not isNewUser:
        if cachedUser != userID:
            try:
                # Try loading existing user state and prolog data
                log.info(f"{userID} was not cached, loading data")
                loadGameStart = time.perf_counter()
                path = GetStateDirectoryName(userID)
                path_to_state = os.path.join(path, "state.p8y")
                ui = load_ui(path_to_state, user_output=funcOut, debug_output=funcDebug)
                perfDict["LoadGameTime"] = time.perf_counter() - loadGameStart

            except LoadException as exception:
                # If we hit an exception we will treat this person like a new user
                isNewUser = True
                log.critical(f"{userID} has a corrupted data file")

        else:
            log.info(f"{userID} was cached, skipping load")

    if isNewUser:
        log.info(f"{userID} is a new user")
        DebugMessage(userID, f"This user is interacting on: {currentWorkItem['Interface']}")
        log.info(f"setting {userID} start game to: {startGame}")
        userDirectory = GetStateDirectoryName(userID)
        path_to_state = os.path.join(userDirectory, "state.p8y")
        if os.path.exists(path_to_state):
            os.remove(path_to_state)
        ui = ui_from_world_name(startGame, user_output=funcOut, debug_output=funcDebug)
        # Send welcome
        # ui.TurnFinished(True)

    else:
        if "NewSession" in currentWorkItem and currentWorkItem["NewSession"] is True:
            OutputMessage("", userID, "",
                          "Welcome back to Perplexity. \nRemember: In this experience, when I'm done describing something, you tell me what you want me to do next. I'll act as your hands and eyes.\n I'll continue where you left off.")

        currentTime = datetime.datetime.now()
        log.info(f"Working on: {userID} - {message}")
        ui.interact_once_across_conjunctions(force_input=message)

    return ui


# Hack for now
def InputMessage(userID, replyTo, prompt):
    return ""


# Collects any output text in the currentWorkItem
def OutputMessage(replyToUserID, userID, replyTo, value):
    global currentWorkItem

    if currentWorkItem is not None:
        replyText = "{}\n".format(value)
        currentWorkItem["Reply"] += replyText
        LogText(userID, replyText)


def DebugMessage(userID, value):
    LogText(userID, "{}\n".format(value))


def LogFileName(userID):
    stateDir = GetStateDirectoryName(userID)
    return os.path.join(stateDir, "user.log")


def EnsureDirectoriesForFile(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def ClearLog(userID):
    log_file = LogFileName(userID)
    EnsureDirectoriesForFile(log_file)
    with open(log_file, "w+") as f:
        f.flush()
        os.fsync(f.fileno())


def LogText(userID, value):
    if value is not None and value.strip() != "":
        log_file = LogFileName(userID)
        EnsureDirectoriesForFile(log_file)
        with open(log_file, "a") as f:
            f.write(value)
            f.flush()
            os.fsync(f.fileno())


def StartP8yStickyScaleService(inputQueue=None, outputQueue=None):
    # Start the webserver
    if outputQueue is not None:
        outputQueue.put("started")

    try:
        app.run(debug=False, host="0.0.0.0", use_reloader=False, port=80)

    except:
        pass

    log.info("Worker exited killing process.")
    sig = getattr(signal, "SIGKILL", signal.SIGTERM)
    os.kill(os.getpid(), sig)


# def P8yStickyScaleVersionTest(inputQueue, outputQueue):
#     serverInit = inputQueue.get(timeout=60)
#     assert serverInit == "started"
#     time.sleep(3)
#
#     exception = False
#     result = None
#     result2 = None
#     result2 = None
#     mailBody = ""
#     result3 = None
#     try:
#         # Generate state using the current version
#         # Start with Baby On Board, which actually starts with a tutorial so we can make sure we don't lose
#         # What game should be played after the tutorial...
#         userID = str(uuid.uuid1())
#         r = urllib.request.urlopen(f'http://localhost:80?From={userID}&ReplyTo=&Game=baby&Body=test', timeout=60)
#         result = r.read()
#         resultDecoded = result.decode("utf-8")
#         initialWorked = "World's Simplest Escape Room" in resultDecoded
#
#         # Update the version number
#         r = urllib.request.urlopen('http://localhost:80/versionsettest', timeout=60)
#         result2 = r.read()
#
#         time.sleep(3)
#
#         # Try again and make sure the convert works and starts with tutorial but then ends and goes to baby on board
#         r = urllib.request.urlopen(f'http://localhost:80?From={userID}&ReplyTo=&Body=end%20the%20tutorial', timeout=60)
#         result3 = r.read()
#         result3Decoded = result3.decode("utf-8")
#         conversionWorked = "Baby on Board" in result3Decoded and "World's Simplest Escape Room" in result3Decoded
#
#     except Exception as err:
#         exception = True
#         mailBody += "\nException calling Perplexity: {}\n".format(str(err))
#
#     except:
#         exception = True
#         mailBody += "\nException calling Perplexity: Unknown\n"
#
#     try:
#         r = urllib.request.urlopen('http://localhost:80/sloppyexit', timeout=60)
#         r.read()
#         time.sleep(8)
#
#     except:
#         pass
#
#     if exception or (result is not None and "Problem ->" in result.decode("utf-8")) or not conversionWorked or not initialWorked:
#         if result is not None:
#             mailBody += result.decode("utf-8")
#         if result2 is not None:
#             mailBody += result2.decode("utf-8")
#         if result3 is not None:
#             mailBody += result3.decode("utf-8")
#         return {"Result": False, "Body": mailBody}
#     else:
#         return {"Result": True}


def P8yStickyScaleSmokeTest(inputQueue, outputQueue):
    serverInit = inputQueue.get(timeout=60)
    assert serverInit == "started"
    time.sleep(3)

    exception = False
    result = None
    result2 = None
    mailBody = ""
    try:
        # First send a message from a known user to make sure it converts
        r = urllib.request.urlopen('http://localhost:80?From=healthcheck&ReplyTo=&Body=Hello!',
                                   timeout=60)
        result = r.read()

        # Then send one from a new user
        r = urllib.request.urlopen('http://localhost:80?From={}&ReplyTo=&Body=Hello!'.format(str(uuid.uuid4())),
                                   timeout=60)
        result2 = r.read()

    except Exception as err:
        exception = True
        mailBody += "\nException calling Perplexity: {}\n".format(str(err))

    except:
        exception = True
        mailBody += "\nException calling Perplexity: Unknown\n"

    # Now close down the server, which throws since it doesn't respond
    # when you "sloppy exit"
    try:
        r = urllib.request.urlopen('http://localhost:80/sloppyexit', timeout=60)
    except:
        pass

    if exception or (result is not None and "Problem ->" in result.decode("utf-8")) or (result2 is not None and "Problem ->" in result2.decode("utf-8")):
        if result is not None:
            mailBody += result.decode("utf-8")
        if result2 is not None:
            mailBody += result2.decode("utf-8")

    else:
        return {"Result": True}

    return {"Result": False, "Body": mailBody}


# Global Settings
# Max number of workitems that can be in the queue at a time
# If more than 2 items are queued, the client performance will be awful
# better to fail in that case.
maxWorkerQueueSize = 2

# How long for Perplexity to try parsing
perplexityMaxParseTimeout = 15

# How long to wait for a message to be sent to a worker
workQueueTimeoutSeconds = 120 + random.randrange(-60, 60)

# How many seconds to wait (including time sitting in the queue) for
# a worker to process a request.
# Give a little time beyond how long Perplexity will take to parse
workerProcessMessageTimeout = perplexityMaxParseTimeout + 5

# Number of seconds we reserve an instance for the user
workerAssignmentTimeoutSeconds = 5 * 60  # 5 minutes, in seconds

# Number of seconds to allow a worker to process a message before we assume it is hung
workerHungSeconds = 60

lastCrashSecondsWindow = 60 * 60 * 2
maxCrashesInWindow = 3

# Track worker process crashes
lastCrash = datetime.datetime.now()
crashCount = 0

log = logging.getLogger("P8yStickyScale")
startGameDefault = "esl"

workerIDs = {}
workerDataMutex = threading.RLock()

waitingThreadsMutex = threading.Lock()
waitingThreads = {}

responseQueue = None
currentWorkItem = None
multiprocessManager = None
response_thread = None

# Logging
# CloudLog(['PrologServer'], logging.DEBUG)
CloudLog(['Pipeline'], logging.DEBUG)
CloudLog(['P8yStickyScale'], logging.DEBUG)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        commandLineCommands = sys.argv[1:]
    else:
        commandLineCommands = []

    if len(commandLineCommands) > 0:
        gameArgs = commandLineCommands[0].split("=")
        if len(gameArgs) == 2 and gameArgs[0].lower() == "game":
            commandLineCommands.pop()
            startGameDefault = gameArgs[1]

    log.info("Starting webserver NO HTTPS")
    app.run(debug=False, host="0.0.0.0", use_reloader=False, port=8000)
