import json
from pathlib import Path
import matplotlib.pyplot as plt
# find all the transcript files
files = list(Path("interview-assignment/dataset").glob("*/transcript.json"))

print("Number of transcripts:", len(files))

# open the first transcript
with open(files[0], "r", encoding="utf-8") as file:
    data = json.load(file)

# get the sentences from the transcript
sentences = data["data"]

# print the first sentence to see what it says
print("First sentence:", sentences[0]["sentence"])

# see who said the first sentence
print("Speaker:", sentences[0]["speaker_name"])

# check the sentiment of that sentence
print("Sentiment:", sentences[0]["sentimentType"])

# go through all the sentences in this meeting
#for item in sentences:
  #  print(item["speaker_name"], ":", item["sentence"])

# count how many sentences are in this meeting
total_sentences = len(sentences)
print("Total sentences in this meeting:", total_sentences)

# start the sentiment counts at zero
positive = 0
negative = 0
neutral = 0

# check the sentiment of each sentence
for item in sentences:
    sentiment = item["sentimentType"]

    if sentiment == "positive":
        positive += 1
    elif sentiment == "negative":
        negative += 1
    elif sentiment == "neutral":
        neutral += 1

# see how many sentences fall under each sentiment
print("Positive:", positive)
print("Negative:", negative)
print("Neutral:", neutral)

# start the total count at zero
all_sentences = 0

# go through all the transcript files
for transcript_file in files:
    # open and read each transcript
    with open(transcript_file, "r", encoding="utf-8") as file:
        meeting = json.load(file)

    # count the sentences in this meeting
    count = len(meeting["data"])
    # add them to the total
    all_sentences += count

print("Total meetings:", len(files))
print("Total sentences:", all_sentences)

# keep track of sentiment from all meetings
total_positive = 0
total_negative = 0
total_neutral = 0

# go through every transcript
for transcript_file in files:
    with open(transcript_file, "r", encoding="utf-8") as file:
        meeting = json.load(file)

    # check every sentence in the meeting
    for item in meeting["data"]:
        sentiment = item["sentimentType"]

        if sentiment == "positive":
            total_positive += 1
        elif sentiment == "negative":
            total_negative += 1
        elif sentiment == "neutral":
            total_neutral += 1

print("Total positive:", total_positive)
print("Total negative:", total_negative)
print("Total neutral:", total_neutral)

# check if the counts match the total sentences
print("Total checked:", total_positive + total_negative + total_neutral)

# calculate sentiment percentages for all meetings
positive_percent = (total_positive / all_sentences) * 100
negative_percent = (total_negative / all_sentences) * 100
neutral_percent = (total_neutral / all_sentences) * 100

# print the results
print(f"Positive: {positive_percent:.2f}%")
print(f"Negative: {negative_percent:.2f}%")
print(f"Neutral: {neutral_percent:.2f}%")

# find the meeting info file for the first transcript
info_file = files[0].parent / "meeting-info.json"

# read the meeting details
with open(info_file, "r", encoding="utf-8") as file:
    meeting_info = json.load(file)

# see the meeting title
print("Meeting title:", meeting_info["title"])

# check the meeting title
title = meeting_info["title"].lower()

if "support" in title:
    print("Meeting category: Support")
elif "internal" in title or "remediation" in title:
    print("Meeting category: Internal")
else:
    print("Meeting category: Needs review")

# see the titles of all meetings
for transcript_file in files:
    info_file = transcript_file.parent / "meeting-info.json"

    with open(info_file, "r", encoding="utf-8") as file:
        info = json.load(file)

    #print(info["title"])

# check the email addresses for this meeting
emails = meeting_info["allEmails"]
print("Participants:", emails)

# see if anyone is from outside the company
outside_emails = []
for email in emails:
    if not email.lower().endswith("@aegiscloud.com"):
        outside_emails.append(email)

print("Outside participants:", outside_emails)

# start counting the meeting types
internal_count = 0
customer_count = 0

# go through all the meetings
for transcript_file in files:
    info_file = transcript_file.parent / "meeting-info.json"

    with open(info_file, "r", encoding="utf-8") as file:
        info = json.load(file)

    # get the participant emails
    emails = info["allEmails"]

    # check if anyone is from outside the company
    outside_emails = []
    for email in emails:
        if not email.lower().endswith("@aegiscloud.com"):
            outside_emails.append(email)

    # count each meeting type
    if len(outside_emails) == 0:
        internal_count += 1
    else:
        customer_count += 1

print("Internal meetings:", internal_count)
print("Customer-facing meetings:", customer_count)
print("Total classified:", internal_count + customer_count)

# count each type of meeting
internal = 0
support = 0
external = 0

# keep track of negative sentences
internal_negative = 0
support_negative = 0
external_negative = 0

# count the sentences for each category
internal_sentences = 0
support_sentences = 0
external_sentences = 0

for transcript_file in files:
    info_file = transcript_file.parent / "meeting-info.json"

    with open(info_file, "r", encoding="utf-8") as file:
        info = json.load(file)

    title = info["title"].lower()
    emails = info["allEmails"]

    # check if anyone is from outside the company
    has_customer = any(
        not email.lower().endswith("@aegiscloud.com")
        for email in emails
    )

    # read the transcript for this meeting
    with open(transcript_file, "r", encoding="utf-8") as file:
        meeting_data = json.load(file)

    # count negative sentences in this meeting
    negative_count = 0
    for item in meeting_data["data"]:
        if item["sentimentType"] == "negative":
            negative_count += 1

    
    # add the counts to each category
    if not has_customer:
        internal += 1
        internal_negative += negative_count
        internal_sentences += len(meeting_data["data"])

    elif title.startswith(("support case", "urgent:", "escalation:")):
        support += 1
        support_negative += negative_count
        support_sentences += len(meeting_data["data"])

    else:
        external += 1
        external_negative += negative_count
        external_sentences += len(meeting_data["data"])


print("Internal:", internal)
print("Support:", support)
print("External:", external)
print("Total:", internal + support + external)

# see the negative counts for each category
print("Internal negative:", internal_negative)
print("Support negative:", support_negative)
print("External negative:", external_negative)
print("Total negative:", internal_negative + support_negative + external_negative)


# check the negative percentage for each category
print(f"Internal negative %: {internal_negative / internal_sentences * 100:.2f}%")
print(f"Support negative %: {support_negative / support_sentences * 100:.2f}%")
print(f"External negative %: {external_negative / external_sentences * 100:.2f}%")

print("Total sentences checked:", internal_sentences + support_sentences + external_sentences)


# create a chart for negative sentiment
categories = ["Support", "Internal", "External"]

percentages = [
    support_negative / support_sentences * 100,
    internal_negative / internal_sentences * 100,
    external_negative / external_sentences * 100
]

# make the bar chart
plt.figure(figsize=(8, 5))
plt.bar(categories, percentages)

plt.title("Negative Sentiment by Meeting Type")
plt.xlabel("Meeting Type")
plt.ylabel("Negative Sentences (%)")

# show percentages above the bars
for i, value in enumerate(percentages):
    plt.text(i, value + 0.5, f"{value:.2f}%", ha="center")

# save the chart
plt.tight_layout()
plt.savefig("negative_sentiment_chart.png")
#plt.show()


# open the summary for the first meeting
summary_file = files[0].parent / "summary.json"

with open(summary_file, "r", encoding="utf-8") as file:
    summary_data = json.load(file)

# see what information the summary has
print("Summary keys:", summary_data.keys())
# see what topics are in this meeting
print("Meeting topics:", summary_data["topics"])

# check how the topics are stored
print("Topics type:", type(summary_data["topics"]))


from collections import Counter

# collect topics from all meetings
all_topics = []

for transcript_file in files:
    summary_file = transcript_file.parent / "summary.json"

    with open(summary_file, "r", encoding="utf-8") as file:
        summary = json.load(file)

    # add the topics from each meeting
    all_topics.extend(summary["topics"])

# count the topics
topic_counts = Counter(all_topics)

# print the top 10 topics
print("Top 10 topics:")

for topic, count in topic_counts.most_common(10):
    print(topic, ":", count)


# see all the different topic names
unique_topics = sorted(topic_counts.keys())

print("Total unique topics:", len(unique_topics))

# we don't need to print every topic anymore
# for topic in unique_topics:
#     print(topic)


# group similar topics together
topic_groups = {
    "Reliability & Incidents": [
        "outage", "incident", "failure", "reliability",
        "backup", "performance", "pipeline", "latency"
    ],
    "Security & Compliance": [
        "compliance", "audit", "soc 2", "pci",
        "security", "hipaa", "gdpr", "threat"
    ],
    "Commercial & Retention": [
        "renewal", "churn", "pricing", "upsell",
        "billing", "invoice", "contract", "retention"
    ],
    "Product & Features": [
        "product", "feature", "roadmap", "launch",
        "sprint", "bug fix", "qa", "ux improvement"
    ],
    "Identity & Integrations": [
        "sso", "saml", "scim", "integration",
        "identity", "mfa", "ldap", "provisioning"
    ]
}


# check the topics in our first meeting
for topic in summary_data["topics"]:
    for group, keywords in topic_groups.items():
        if any(word in topic.lower() for word in keywords):
            print(topic, "->", group)


# start counting each topic group
group_counts = {group: 0 for group in topic_groups}
unmatched_meetings = 0

# go through all the meetings
for transcript_file in files:
    summary_file = transcript_file.parent / "summary.json"

    with open(summary_file, "r", encoding="utf-8") as file:
        summary = json.load(file)

    # keep track of groups found in this meeting
    matched_groups = set()

    # check which groups the topics belong to
    for topic in summary["topics"]:
        for group, keywords in topic_groups.items():
            if any(word in topic.lower() for word in keywords):
                matched_groups.add(group)

    # count each group once per meeting
    for group in matched_groups:
        group_counts[group] += 1

    # check meetings that didn't match any group
    if not matched_groups:
        unmatched_meetings += 1


print("Meetings by topic group:")

for group, count in group_counts.items():
    print(group, ":", count)

print("Meetings without a match:", unmatched_meetings)


# check which meetings we missed
for transcript_file in files:
    summary_file = transcript_file.parent / "summary.json"
    info_file = transcript_file.parent / "meeting-info.json"

    with open(summary_file, "r", encoding="utf-8") as file:
        summary = json.load(file)

    with open(info_file, "r", encoding="utf-8") as file:
        info = json.load(file)

    # check whether any topic matches our groups
    found_match = False

    for topic in summary["topics"]:
        for keywords in topic_groups.values():
            if any(word in topic.lower() for word in keywords):
                found_match = True

    if not found_match:
        print("Unmatched meeting:", info["title"])
        print("Topics:", summary["topics"])


# check action items across all meetings
total_actions = 0
meetings_with_actions = 0
risk_actions = []

# words that might point to urgent follow-ups
risk_keywords = [
    "outage", "incident", "escalation",
    "urgent", "churn", "renewal risk",
    "failure", "customer impact"
]

for transcript_file in files:
    summary_file = transcript_file.parent / "summary.json"

    with open(summary_file, "r", encoding="utf-8") as file:
        summary = json.load(file)

    actions = summary.get("actionItems", [])

    total_actions += len(actions)

    if actions:
        meetings_with_actions += 1

    # look for possible risk-related actions
    for action in actions:
        action_text = str(action)

        if any(word in action_text.lower() for word in risk_keywords):
            risk_actions.append(action_text)

print("\nAction item analysis")
print("Total action items:", total_actions)
print("Meetings with action items:", meetings_with_actions)
print("Potential risk-related action items:", len(risk_actions))

# show a few examples
print("\nExamples of risk-related actions:")
for action in risk_actions[:5]:
    print("-", action)


# create the topic distribution chart
topic_names = list(group_counts.keys())
topic_values = list(group_counts.values())

plt.figure(figsize=(10, 5))
plt.barh(topic_names, topic_values)

plt.title("Topic Distribution Across 100 Meetings")
plt.xlabel("Number of Meetings")

# add numbers next to the bars
for i, value in enumerate(topic_values):
    plt.text(value + 1, i, str(value), va="center")

plt.xlim(0, max(topic_values) + 10)
plt.tight_layout()

# save the chart
plt.savefig("topic_distribution_chart.png")
plt.close()
