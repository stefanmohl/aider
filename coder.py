#!/usr/bin/env python

import os
import sys
import copy
import random
import json

from pathlib import Path
from collections import defaultdict

import os
import openai

from dump import dump

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt_webdev = '''
I want you to act as a web development expert.
I want you to answer only with code.
Make the requested change to the provided code and output the changed code.
MAKE NO OTHER CHANGES!
Do not provide explanations!
'''

class Chat:
    fnames = []
    def system(self, prompt):
        self.system_prompt = prompt
    def file(self, fname):
        self.fnames.append(fname)
    def request(self, prompt):
        self.request_prompt = prompt

    def quoted_file(self, fname):
        prompt = '\n'
        prompt += fname.name
        prompt += '\n```\n'
        prompt += fname.read_text()
        prompt += '\n```\n'
        return prompt

    def setup(self):
        prompt = ''
        for fname in self.fnames:
            prompt += self.quoted_file(fname)

        prompt += '\n###\n'
        prompt += self.request_prompt

        self.prompt = prompt

    def send(self, messages):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
            stream = True,
        )
        resp = []
        for chunk in completion:
            try:
                text = chunk.choices[0].delta.content
                resp.append(text)
            except AttributeError:
                continue
            sys.stdout.write(text)
            sys.stdout.flush()

        print()
        print('='*40)

        resp = ''.join(resp)
        return resp

    def update_files(self):
        random.shuffle(self.fnames)
        for fname in self.fnames:
            self.update_file(fname)

    def update_file(self, fname):
        prompt = self.prompt
        prompt += f'''
Output the updated version of {fname.name}
'''

        messages = [
            dict(role = 'system', content = self.system_prompt),
            dict(role = 'user', content = prompt),
        ]

        content = chat.send(messages)
        if content.strip() == 'NONE':
            return

        lines = content.splitlines()
        if lines[0].startswith(fname.name):
            lines = lines[1:]
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines[-1].startswith('```'):
            lines = lines[:-1]
        fname.write_text('\n'.join(lines))

chat = Chat()

chat.system(prompt_webdev)

dname = Path('../easy-chat')
chat.file(dname / 'index.html')
chat.file(dname / 'chat.css')
chat.file(dname / 'chat.js')

#for fname in chat.fnames:
#    print(chat.quoted_file(fname))
#sys.exit()

chat.request('''
Right now the speaker icons come after the text in each speech bubble.
Move all the speaker icons so they come before the text.
''')

chat.setup()
chat.update_files()
