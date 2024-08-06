import json
import logging
import os
import threading
from datetime import datetime
import openai
from perplexity.utilities import ShowLogging

# Background from here: https://platform.openai.com/docs/guides/chat-completions
# Setup: You need to set up your API key as an environment variable
#       export OPENAI_API_KEY='your-api-key-here'


# Requires some kind of user_id that is unique (like a guid)
# predication - some string that represents the predication this is emulating. Used to cache the values
# phrase - a phrase phrased like a yes or no question like "Are dogs an animal?"
def StartOpenAIBooleanRequest(user_id, predication, phrase, cache_answers=True):
    phrase = phrase.strip()
    response = []
    response_thread = threading.Thread(target=ResponseThread,
                                       args=[user_id, predication, BooleanCompletionApproach, BooleanCompletionApproachResponseCleaner, BooleanValidateResponse, phrase, response, cache_answers])
    response_thread.start()
    return {"Thread": response_thread, "Response": response, "UserID": user_id}


# An "approach" implements the way we are going to interact with ChatGPT.
# In this case, by asking a yes/no question of some kind
def BooleanCompletionApproach(user_id, phrase):
    prompt = "Answer just yes or no: " + phrase
    return client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a intelligent assistant. Answer only with the word 'yes' or the word 'no'"},
                        {"role": "user", "content": prompt}
                    ],
                    user=user_id
    )


def BooleanCompletionApproachResponseCleaner(response):
    if len(response) > 0:
        response = response.strip()

        if "\n" in response:
            gptLogger.debug(f"GPT: incorrect format{response}, ignoring: {response}")
            return None

        if response.lower() in ["yes", "true"]:
            return "true"

        elif response.lower() in ["no", "false"]:
            return "false"

        else:
            gptLogger.debug(f"GPT: incorrect format, ignoring: {response}")
            return None

    else:
        gptLogger.debug(f"GPT: returned nothing, ignoring: {response}")
        return None


def BooleanValidateResponse(approachResponseCleaner, phrase, response):
    phrase = phrase.strip(" \n")

    replacement = approachResponseCleaner(response)
    if replacement is None or replacement is False:
        return replacement

    # Just adding a period should be ignored
    if phrase[-1] not in ["!", "."] and replacement[-1] in ["!", "."]:
        replacement = replacement[0:-1]

    if phrase.lower() == replacement.lower():
        gptLogger.debug(f"GPT: AI returned same string.")
        return False

    else:
        return replacement


# Returns whether the request is complete or not without waiting
def IsOpenAIRequestComplete(response_thread):
    return not response_thread["Thread"].is_alive()


# Returns:
#   None if there was a failure or if we got bogus data from OpenAI
#   Otherwise: whatever the appropriate response is from OpenAI
def CompleteOpenAIRequest(response_thread, wait=False):
    if wait and isinstance(wait, int):
        response_thread["Thread"].join(wait)

    else:
        response_thread["Thread"].join()

    if not IsOpenAIRequestComplete(response_thread):
        CaptureDebug(response_thread["UserID"], f"GPT: not complete - returning None.")
        return None

    else:
        CaptureDebug(response_thread["UserID"], f"GPT: complete - returning '{response_thread['Response'][0]}'.")

    return response_thread["Response"][0]


# Main routine that does the OpenAI processing
def ResponseThread(user_id, predication, approachFunc, approachResponseCleaner, approachValidator, phrase, response, cacheResponses, ignoreCache=False):
    global intentionallyFail
    global openAICache
    global openAICacheMutex
    global latestFailures

    gptLogger.debug(f"GPT: using user: {user_id}")

    cacheKey = f"{approachFunc.__name__}({predication}): {StripPunctuation(phrase)}"
    try:
        if phrase.strip() == "":
            # Just return False
            response.append(False)

        else:
            cachedValue = None
            if not ignoreCache:
                with openAICacheMutex:
                    cachedValue = openAICache.get(cacheKey, None)

            if cachedValue is not None:
                response.append(cachedValue)
                CaptureDebug(user_id, f"GPT: cached value for {phrase}: {cachedValue}")
                return

            if IsServiceDown():
                CaptureDebug(user_id, f"GPT: service down")
                response.append(None)
                return

            # Actually call the function to send the phrase to OpenAI
            result = approachFunc(user_id, phrase)

            if intentionallyFail:
                raise Exception("GPT: Failing on purpose")

            if result is not None and len(result.choices) > 0:
                correction = result.choices[0].message.content
                validResponse = approachValidator(approachResponseCleaner, phrase, correction)
                response.append(validResponse)
                CaptureDebug(user_id, f"GPT: Response is '{validResponse}'")

            else:
                CaptureDebug(user_id, f"GPT: failed: {result}")
                response.append(None)

    except Exception as e:
        CaptureDebug(user_id, f"GPT: exception: {e}")
        response.append(None)
        latestFailures.append(datetime.now())

    if not ignoreCache and cacheResponses and response[0] is not None:
        with openAICacheMutex:
            openAICache[cacheKey] = StripPunctuation(response[0]) if response[0] is not False else False
            try:
                with open(CachePath(), "w") as file:
                    file.write(json.dumps(openAICache, indent=0))

            except Exception as e:
                CaptureDebug(user_id, f"GPT: exception storing cache: original: {phrase} fixed: {response[0]}")


def StripPunctuation(phrase):
    return phrase.strip(".?! ")


def CaptureDebug(user_id, msg):
    gptLogger.debug(msg)


def IntentionallyFailGPT(value):
    global intentionallyFail
    global latestFailures

    intentionallyFail = value
    if intentionallyFail is False:
        latestFailures = []


def CachePath():
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(scriptPath, "OpenAICache.txt")


def IsServiceDown():
    now = datetime.now()
    count = len(latestFailures)
    index = 0
    for _ in range(count):
        if (now - latestFailures[index]).total_seconds() > failurePeriodSeconds:
            del latestFailures[index]
        else:
            index += 1

    return len(latestFailures) > failureCountLimit


gptLogger = logging.getLogger('ChatGPT')
intentionallyFail = False
openAICacheMutex = threading.Lock()

with openAICacheMutex:
    with open(CachePath()) as file:
        openAICache = json.loads(file.read())


# Holds the timestamp for failures in the last failurePeriodSeconds
# Every time it is checked we delete the entries that are older than failurePeriodSeconds
# If the remaining count >= failureCountLimit we stop trying
# Each entry is a timestamp
failurePeriodSeconds = 10 * 60
failureCountLimit = 5
latestFailures = []


client = openai.OpenAI()


if __name__ == '__main__':
    # from openai import OpenAI
    # import os
    # models = client.models.list()
    # print(models.data)


    ShowLogging("Pipeline")
    user_id = "test"
    request_info = StartOpenAIBooleanRequest(user_id,
                                             "is_food_or_drink_predication",
                                             "Is an apple either a food or a drink?",
                                             cache_answers=False)

    # Give OpenAI 10 seconds to respond (might be too long for production use, just a test)
    print(CompleteOpenAIRequest(request_info, wait=10))

    # phrase ="Is a hamburger either a food or drink?"
    # user_id = "tets"
    # prompt = "Answer just yes or no: " + phrase
    # result = client.chat.completions.create(
    #                 model="gpt-4o",
    #                 messages=[
    #                     {"role": "system", "content": "You are a intelligent assistant."},
    #                     {"role": "user", "content": prompt}
    #                 ],
    #                 # temperature=1,
    #                 # n=1,
    #                 user=user_id
    # )
    #
    # print(result)



