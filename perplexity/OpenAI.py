import json
import logging
import os
import threading
from datetime import datetime
import openai
from perplexity.utilities import ShowLogging


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


# Returns whether the request is complete or not without waiting
def IsOpenAIRequestComplete(response_thread):
    return not response_thread["Thread"].is_alive()


# Returns:
#   None if there was a failure or we got bogus data from OpenAI
#   Otherwise: whatever the appropriate response is from OpenAI
def CompleteOpenAIRequest(response_thread, wait=False):
    if wait and isinstance(wait, int):
        response_thread["Thread"].join(wait)
    else:
        response_thread["Thread"].join()

    if not IsOpenAIRequestComplete(response_thread):
        CaptureDebug(response_thread["UserID"], f"GPT3: not complete - returning None.")
        return None

    else:
        CaptureDebug(response_thread["UserID"], f"GPT3: complete - returning '{response_thread['Response'][0]}'.")

    return response_thread["Response"][0]


# Main routine that does the OpenAI processing
def ResponseThread(user_id, predication, approachFunc, approachResponseCleaner, approachValidator, phrase, response, cacheFixes, ignoreCache=False):
    global intentionallyFail
    global openAICache
    global openAICacheMutex
    global latestFailures

    pipelineLogger.debug(f"GPT3: using user: {user_id}")

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
                CaptureDebug(user_id, f"GPT3: cached value: {cachedValue}")
                return

            if IsServiceDown():
                CaptureDebug(user_id, f"GPT3: service down")
                response.append(None)
                return

            if SafeContent(user_id, phrase):
                # Actually call the function to send the phrase to OpenAI
                result = approachFunc(user_id, phrase)

            else:
                result = None
                CaptureDebug(user_id, f"GPT3: flagged for moderation input text: {phrase}")
                response.append(None)

            if intentionallyFail:
                raise Exception("GPT3: Failing on purpose")

            if result is not None and "choices" in result and len(result["choices"]) > 0 and "text" in result["choices"][0]:
                correction = result["choices"][0]["text"]
                if SafeContent(user_id, correction):
                    validResponse = approachValidator(approachResponseCleaner, phrase, correction)
                    response.append(validResponse)
                    CaptureDebug(user_id, f"GPT3: Corrected response is '{validResponse}'")
                else:
                    CaptureDebug(user_id, f"GPT3: flagged for moderation: {correction}")
                    response.append(None)

            else:
                CaptureDebug(user_id, f"GPT3: failed: {result}")
                response.append(None)

    except Exception as e:
        CaptureDebug(user_id, f"GPT3: exception: {e}")
        response.append(None)
        latestFailures.append(datetime.now())

    if not ignoreCache and cacheFixes and response[0] is not None:
        with openAICacheMutex:
            openAICache[cacheKey] = StripPunctuation(response[0]) if response[0] is not False else False
            try:
                with open(CachePath(), "w") as file:
                    file.write(json.dumps(openAICache, indent=0))
            except Exception as e:
                CaptureDebug(user_id, f"GPT3: exception storing cache: original: {phrase} fixed: {response[0]}")


def BooleanCompletionApproach(user_id, phrase):
    global separator, end
    phrase = "Answer just yes or no: " + phrase
    prompt = FormatPrompt(phrase, separator)

    return openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        best_of=1,
        stop=[end],
        user=user_id
    )


def strip_all_end(text, suffix):
    while text.endswith(suffix):
        text = text[:-len(suffix)]
    return text


def strip_all_start(text, prefix):
    while text.startswith(prefix):
        text = text[len(prefix):]
    return text


def strip_all(text, findText):
    return strip_all_start(strip_all_end(text, findText), findText)


def BooleanCompletionApproachResponseCleaner(response):
    global end
    if len(response) > 0:
        response = response.strip()

        if "\n" in response:
            pipelineLogger.debug(f"GPT3: incorrect format, ignoring: {response}")
            return None

        if response.lower() in ["yes", "true"]:
            return "true"

        elif response.lower() in ["no", "false"]:
            return "false"

        else:
            # Only pay attention when the answer is surrounded by quotes since that indicates
            # it is not going off the rails
            pipelineLogger.debug(f"GPT3: incorrect format, ignoring: {response}")
            return None

    else:
        pipelineLogger.debug(f"GPT3: returned nothing, ignoring: {response}")
        return None


def StripPunctuation(phrase):
    return phrase.strip(".?! ")


def SafeContent(user_id, text):
    return ClassifyContent(user_id, text) < 2


# From: https://beta.openai.com/docs/models/content-filter
# We generally recommend not returning to end-users any completions that the Content Filter has flagged with an output of 2
def ClassifyContent(user_id, content_to_classify):
    response = openai.Completion.create(
        model="content-filter-alpha",
        prompt="<|endoftext|>" + content_to_classify + "\n--\nLabel:",
        temperature=0,
        max_tokens=1,
        top_p=0,
        logprobs=10,
        user=user_id
    )
    output_label = response["choices"][0]["text"]

    # This is the probability at which we evaluate that a "2" is likely real
    # vs. should be discarded as a false positive
    toxic_threshold = -0.355

    if output_label == "2":
        # If the model returns "2", return its confidence in 2 or other output-labels
        logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]

        # If the model is not sufficiently confident in "2",
        # choose the most probable of "0" or "1"
        # Guaranteed to have a confidence for 2 since this was the selected token.
        if logprobs["2"] < toxic_threshold:
            logprob_0 = logprobs.get("0", None)
            logprob_1 = logprobs.get("1", None)

            # If both "0" and "1" have probabilities, set the output label
            # to whichever is most probable
            if logprob_0 is not None and logprob_1 is not None:
                if logprob_0 >= logprob_1:
                    output_label = "0"
                else:
                    output_label = "1"
            # If only one of them is found, set output label to that one
            elif logprob_0 is not None:
                output_label = "0"
            elif logprob_1 is not None:
                output_label = "1"

            # If neither "0" or "1" are available, stick with "2"
            # by leaving output_label unchanged.

    # if the most probable token is none of "0", "1", or "2"
    # this should be set as unsafe
    if output_label not in ["0", "1", "2"]:
        output_label = "2"

    return int(output_label)


def CaptureDebug(user_id, msg):
    pipelineLogger.debug(msg)


def BooleanValidateResponse(approachResponseCleaner, phrase, response):
    global end
    global separator
    global ignoreTokens
    allPunctuation = ["?", "!", "."]
    phrase = phrase.strip(" \n")

    # replacement should == just the raw text at this point (i.e. not
    # have quotes around it or " END"
    replacement = approachResponseCleaner(response)
    if replacement is None or replacement is False:
        return replacement

    # If the end tokens are still in there, it is bogus
    for token in ignoreTokens:
        if token in response:
            pipelineLogger.debug(f"GPT3: invalid response: {response}")
            return None

    # Just adding a period should be ignored
    if phrase[-1] not in ["!", "."] and replacement[-1] in ["!", "."]:
        replacement = replacement[0:-1]

    if phrase.lower() == replacement.lower():
        pipelineLogger.debug(f"GPT3: AI returned same string.")
        return False
    else:
        return replacement

    pipelineLogger.debug(f"GPT3: invalid response: {response}")
    return None


def IntentionallyFailGPT3(value):
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


def FormatPrompt(prompt, separator):
    return f'"{prompt}"{separator}'


openai.api_key = os.getenv("OPENAIKEY")
pipelineLogger = logging.getLogger('Pipeline')
intentionallyFail = False
openAICacheMutex = threading.Lock()

with openAICacheMutex:
    with open(CachePath()) as file:
        openAICache = json.loads(file.read())

separator = "\n\n###\n\n"
end = " END"
ignoreTokens = [separator, end, "###", " END"]

# Holds the timestamp for failures in the last failurePeriodSeconds
# Every time it is checked we del the entries that are older than failurePeriodSeconds
# If the remaining count >= failureCountLimit we stop trying
# Each entry is a timestamp
failurePeriodSeconds = 10 * 60
failureCountLimit = 5
latestFailures = []


if __name__ == '__main__':
    ShowLogging("Pipeline")
    user_id = "test"
    request_info = StartOpenAIBooleanRequest(user_id, "food_contain_predication", "Does a salad sometimes contain nuts?")

    # Give OpenAI 10 seconds to respond (might be too long for production use, just a test)
    print(CompleteOpenAIRequest(request_info, wait=10))



