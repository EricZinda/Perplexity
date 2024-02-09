# This file implements storage in aws for
# when perplexity is run as a service in the aws cloud
# Set the environment variable "DONTUSECLOUD" to use a local mock instead of going to the cloud
# Set credentials using the boto environment variables or Shared credential file: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
import filecmp
import logging
import os
import sys
import uuid
from io import BytesIO
import boto3


# Used when the data changed out from under us
# Which never happens with AWS
class WriteConflict(Exception):
    pass


class NoSuchKey(Exception):
    pass


# Good how-to: https://hands-on.cloud/working-with-s3-in-python-using-boto3/
# Consistency: https://aws.amazon.com/s3/consistency/
# Object reference that shows how to use Etags: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.get
class CloudState:
    def __init__(self, project, bucketName):
        self.bucketName = bucketName
        localOnlyEnv = os.getenv('DONTUSECLOUD')
        if localOnlyEnv is None:
            AWS_REGION = "us-east-1"
            self.client = boto3.client("s3", region_name=AWS_REGION)
        else:
            print("WARNING: Using local mock since DONTUSECLOUD is set")
            self.client = None

        # Used if initialized with no credentials for testing
        self.localStore = {}

    # Writes the blob stored for this key into the file at pathForBlob
    # returns a dict with some metadata including the generation of the file
    # that is used for concurrency checking
    def Read(self, key, pathForBlob):
        if self.client is None:
            try:
                with open(pathForBlob, "wb") as download_file:
                    download_file.write(self.__ReadLocal(key))
                return {"Key": key, "Generation": 1}
            except NoSuchKey:
                return None
        else:
            try:
                response = self.client.get_object(Bucket=self.bucketName, Key=key)
                with open(pathForBlob, "wb") as file:
                    file.write(response["Body"].read())
                return {"Key": key, "Generation": response["ETag"]}
            except self.client.exceptions.NoSuchKey:
                return None

    def __ReadLocal(self, key):
        if key not in self.localStore:
            raise NoSuchKey

        return self.localStore[key]

    def CreateNew(self, key):
        return {"Key": key, "Generation": 0}

    # No generation is ignored since AWS doesn't have generations
    def Save(self, dataInfo, pathToNewBlob, noGeneration=False):
        if self.client is None:
            with open(pathToNewBlob, "rb") as data:
                self.__SaveLocal(dataInfo["Key"], data.read())
            return True

        with open(pathToNewBlob, "rb") as file:
            currentValue = file.read()

        response = self.client.put_object(Bucket=self.bucketName, Key=dataInfo["Key"], Body=BytesIO(currentValue))
        dataInfo["Generation"] = response["ETag"]

        return True

    def __SaveLocal(self, key, data):
        self.localStore[key] = data

    # Only works if it does exist and returns True, otherwise False if it doesn't exist
    # or Exception if optimistic failed
    def AppendLog(self, key, pathToFile):
        if self.client is None:
            return True

        # Get the current value
        try:
            response = self.client.get_object(Bucket=self.bucketName, Key=key)
            currentValue = response["Body"].read()
        except self.client.exceptions.NoSuchKey:
            return False

        # Concat it with the new value
        with open(pathToFile, "rb") as file:
            currentValue += file.read()

        # Update it
        self.client.put_object(Bucket=self.bucketName, Key=key, Body=BytesIO(currentValue))

        return True

    # Different from GoogleState: Will replace if it exists
    def CreateLog(self, key, pathToFile):
        if self.client is None:
            return

        with open(pathToFile, "rb") as file:
            currentValue = file.read()
            self.client.put_object(Bucket=self.bucketName, Key=key, Body=BytesIO(currentValue))

    # Eventually works for all cases
    def CreateOrAppendLog(self, key, pathToFile):
        # If someone updated or created before us,
        # keep trying forever until we get our log entry in there
        while True:
            if self.AppendLog(key, pathToFile):
                return
            elif self.CreateLog(key, pathToFile):
                return

    # Ensures that there is a state file at rawStatePath
    # either loaded from the server, or created (if the user is new)
    # an information dictionary is returned for concurrency use
    def LoadState(self, userID, rawStatePath):
        value = self.Read(userID, rawStatePath)
        if value is None:
            value = self.CreateNew(userID)
            value["NewUser"] = True
        else:
            value["NewUser"] = False

        # If no exceptions happened, we now have loaded the data
        return value


def CloudLog(topicList, level):
    formatter = logging.Formatter('%(name)s %(asctime)s: %(message)s')
    cloudHandler = None
    fileHandler = logging.StreamHandler(sys.stdout)
    fileHandler.setFormatter(formatter)

    for topic in topicList:
        topicLogger = logging.getLogger(topic)
        topicLogger.setLevel(level)
        if cloudHandler is not None:
            topicLogger.addHandler(cloudHandler)
        topicLogger.addHandler(fileHandler)


if __name__ == '__main__':
    #
    # Smoke tests
    #
    fileOut = os.path.join(os.path.dirname(os.path.realpath(__file__)), "testOut.dat")
    fileIn = os.path.join(os.path.dirname(os.path.realpath(__file__)), "testIn.dat")
    userStateOut = os.path.join(os.path.dirname(os.path.realpath(__file__)), "userstate.dat")
    if os.path.exists(userStateOut):
        os.remove(userStateOut)

    testKey = "Test-" + uuid.uuid4().hex
    testValue = uuid.uuid4().hex.encode('utf-8')
    testValue2 = uuid.uuid4().hex.encode('utf-8')
    testValue3 = uuid.uuid4().hex.encode('utf-8')
    state = CloudState(project=None, bucketName="perplexityusers")

    # Key doesn't exist yet, returns None
    value = state.Read(testKey, fileIn)
    assert value is None

    # Create a fake initial value
    with open(fileOut, "wb") as file:
        file.write(testValue)

    # Initialize the file
    dataInfo = state.CreateNew(testKey)
    assert dataInfo["Generation"] == 0

    # Save the initial file, should change the generation
    assert state.Save(dataInfo, fileOut) is True
    assert dataInfo["Generation"] != 0

    # This doesn't work on AWS since they don't allow
    # atomic "check then update if the same"
    # # Save it again (should fail since one exists now)
    # assert state.Save(dataInfo, fileOut) is False

    # Get the initial value
    dataInfo = state.Read(testKey, fileIn)
    assert dataInfo is not None
    assert filecmp.cmp(fileOut, fileIn, shallow=False)
    oldGeneration = dataInfo["Generation"]

    # Update it, should have a different generation
    with open(fileOut, "wb") as file:
        file.write(testValue2)
    assert state.Save(dataInfo, fileOut) is True
    assert dataInfo["Generation"] != oldGeneration
    oldGeneration = dataInfo["Generation"]

    # Make sure it worked, should be the same generation
    dataInfo = state.Read(testKey, fileIn)
    assert dataInfo is not None
    assert filecmp.cmp(fileOut, fileIn, shallow=False)
    assert dataInfo["Generation"] == oldGeneration

    userKey = "User-" + uuid.uuid4().hex
    logKey = "Log-" + uuid.uuid4().hex
    logKey2 = "Log-" + uuid.uuid4().hex
    logValue1 = uuid.uuid4().hex.encode('utf-8')
    logValue2 = uuid.uuid4().hex.encode('utf-8')

    with open(fileOut, "wb") as file:
        file.write(logValue1)

    # Log doesn't exist, should fail
    assert state.AppendLog(logKey, fileOut) is False

    # Create should work the first time (i.e. not throw)
    state.CreateLog(logKey, fileOut)

    # This doesn't work on AWS since they don't allow
    # atomic "check then update if the same"
    # # But throw the second time
    # exception = False
    # try:
    #     state.CreateLog(logKey, fileOut)
    # except PreconditionFailed:
    #     exception = True
    # assert exception is True

    # Append should work now
    assert state.AppendLog(logKey, fileOut) is True

    # CreateOrAppend should work on an existing key
    state.CreateOrAppendLog(logKey, fileOut)

    # CreateOrAppend should work on a new key
    state.CreateOrAppendLog(logKey2, fileOut)

    # Should create a new user the first time through
    # But not a file
    dataInfo = state.LoadState(userKey, userStateOut)
    assert dataInfo["NewUser"] is True
    assert dataInfo["Generation"] == 0
    assert os.path.exists(userStateOut) is False

    # Create and save the file, should have a new generation
    with open(userStateOut, "wb") as file:
        file.write(userKey.encode())
    state.Save(dataInfo, userStateOut)
    assert dataInfo["Generation"] != 0
    oldGeneration = dataInfo["Generation"]

    # Should load now
    os.remove(userStateOut)
    dataInfo = state.LoadState(userKey, userStateOut)
    assert dataInfo["NewUser"] is False
    assert dataInfo["Generation"] == oldGeneration
    assert os.path.exists(userStateOut) is True
    with open(userStateOut, "rb") as file:
        result = file.read()
        assert result == userKey.encode()
