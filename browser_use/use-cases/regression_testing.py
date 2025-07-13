"""
Goal: Conduct regerssion testing using stories pulled from Jira


Simple try of the agent.
@dev You need to add OPENAI_API_KEY to your environment variables.
"""

import asyncio
import os
import sys
from base64 import b64encode

import httpx
from pydantic import BaseModel

from browser_use import Controller
from browser_use.agent.service import Agent
from browser_use.helpers.extract_acceptance_criteria import extract_acceptance_criteria

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv()

from browser_use.llm import ChatOpenAI

if not os.getenv('OPENAI_API_KEY'):
	raise ValueError('OPENAI_API_KEY is not set. Please add it to your environment variables.')

controller = Controller()


class JiraStory(BaseModel):
	story_key: str
	summary: str
	criteria: list[str]


# Replace these:
JIRA_EMAIL = 'mustafaalkaysi@gmail.com'
API_TOKEN = os.getenv('JIRA_API_KEY')
JIRA_DOMAIN = 'mustafa-alkaysi.atlassian.net'

JQL = 'project = TEST'

# Jira API URL
url = f'https://{JIRA_DOMAIN}/rest/api/3/search'

auth_str = f'{JIRA_EMAIL}:{API_TOKEN}'
basic_auth = b64encode(auth_str.encode()).decode()


headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Basic {basic_auth}'}
params = {'jql': JQL, 'fields': 'summary,description,attachment', 'maxResults': 50}


async def main():
	llm = ChatOpenAI(model='gpt-4.1')

	with httpx.Client() as client:
		response = client.get(url, headers=headers, params=params)
		if response.status_code == 200:
			issues = response.json()['issues']
		else:
			print(f'Error: {response.status_code} - {response.text}')

	stories = []
	for issue in issues:
		key = issue['key']
		summary = issue['fields']['summary']
		criteria = extract_acceptance_criteria(issue['fields']['description'])
		stories.append({'Story': {'story_key': key, 'summary': summary, 'criteria': criteria}})

	agents = []
	for story in stories:
		task = f'Go to https://deloitte.com.For each {story} provided, check the acceptance criteria.Is it met? Respond PASS or FAIL. Each story needs to be tested completely separate. AC needs to be tested exactly for it to PASS.'
		agent = Agent(task=task, llm=llm, controller=controller)
		agents.append(agent)

	await asyncio.gather(*[agent.run() for agent in agents])

	input('Press Enter to exit')


if __name__ == '__main__':
	asyncio.run(main())
