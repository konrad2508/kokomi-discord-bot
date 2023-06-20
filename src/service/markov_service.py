import datetime
import random
import re

from nextcord import TextChannel, Object, Message

from model.exception.channel_not_learned import ChannelNotLearned
from model.exception.no_new_messages import NoNewMessages
from model.exception.not_enough_data import NotEnoughData
from model.markov.markov_grammar import MarkovGrammar


class MarkovService:
    '''Class responsible for operating the Markov chain model.'''

    def __init__(self) -> None:
        self.grammars: dict[int, MarkovGrammar] = {}
        self.sentence_starts: dict[int, set[str]] = {}
        self.newest_message: dict[int, int] = {}
        self.gram_n = 2
        self.max_message_length = 500

    async def learn(self, channel: TextChannel) -> int:
        '''Learns the model for a specified channel. Returns bool value indicating success or failure.'''

        if channel.id in self.newest_message:
            messages = [ msg async for msg in channel.history(oldest_first=False, limit=None, after=Object(self.newest_message[channel.id])) ]
        
        else:
            messages = [ msg async for msg in channel.history(oldest_first=False, limit=None) ]

        if len(messages) == 0:
            raise NoNewMessages

        # 0. merge messages from the same person occuring after each other in a short period of time
        messages_content = self._merge_messages(messages)
        
        self.newest_message[channel.id] = messages[0].id

        # 1. filter messages - command invokations, hyperlinks, mentions etc
        filtered_messages = self._filter_messages(messages_content)

        # 2. tokenize messages
        tokenized_messages = [ [ m for m in msg.split(' ') if m != '' ] for msg in filtered_messages ]

        # 2.1. generate n-grams
        ngrams = self._generate_ngrams(tokenized_messages)

        # 3. create and save grammar
        if channel.id not in self.grammars:
            self.grammars[channel.id] = MarkovGrammar()
            self.sentence_starts[channel.id] = set()
        
        for n in ngrams:
            for m in n:
                splitted = m.split(' ')

                input = ' '.join(splitted[:-1])
                
                input = self._normalize_input(input)
                output = m

                self.grammars[channel.id] += [input, output]

        # 4. save sentence start - use original, unmerged messages
        messages_original_content = [ msg.content for msg in messages ]
        filtered_original_messages = self._filter_messages(messages_original_content)
        tokenized_original_messages = [ [ m for m in msg.split(' ') if m != '' ] for msg in filtered_original_messages ]
        original_ngrams = self._generate_ngrams(tokenized_original_messages)

        for n in original_ngrams:
            splitted_first_ngram = n[0].split(' ')

            normalized_sentence_start = self._normalize_input(' '.join(splitted_first_ngram[:-1]))
            self.sentence_starts[channel.id].add(normalized_sentence_start)
        
        # 5. verify
        # self.grammars[channel.id].print_matrixes()
        # print(self.sentence_starts[channel.id])

        return len(messages)
    
    async def say(self, channel: TextChannel) -> str:
        if channel.id not in self.grammars:
            raise ChannelNotLearned

        if len(self.sentence_starts[channel.id]) == 0:
            raise NotEnoughData

        # choose a starting ngram
        starting = random.choice(tuple(self.sentence_starts[channel.id]))

        # generate a poem
        generated_message = starting

        try:
            while len(generated_message) < self.max_message_length:
                input = ' '.join(generated_message.split(' ')[1 - self.gram_n:])
                
                input = self._normalize_input(input)
                output = self.grammars[channel.id][input]

                generated_message = f'{" ".join(generated_message.split(" ")[:1 - self.gram_n])} {output}'
        
        finally:
            return generated_message
    
    def _merge_messages(self, messages: list[Message]) -> list[str]:
        messages_content = []
        last_message = messages[-1]
        message_content = messages[-1].content

        for msg in messages[-2::-1]:
            # check if same author and created at the same time
            if msg.author != last_message.author or msg.created_at - last_message.created_at > datetime.timedelta(minutes=5):
                messages_content.append(message_content)

                last_message = msg
                message_content = msg.content

                continue
            
            # else merge messages
            message_content = f'{message_content} {msg.content}'
        
        messages_content.append(message_content)

        return messages_content

    def _filter_messages(self, messages: list[str]) -> list[str]:
        # remove hyperlinks
        messages = [ re.sub(r'(?:https?|ftp)\:\/\/.*?(?:$|\s)', '', msg)      for msg in messages ]

        # remove command invokations, mentions, tags etc
        messages = [ re.sub(r'(?:^|\s)[!<$%^&*\-\+=\?\/\.\,][^\s]+', '', msg) for msg in messages ]

        return messages


    def _generate_ngrams(self, tokenized_messages: list[list[str]]) -> list[list[str]]:
        ngrams = [ zip(*[ tokenized[i:] for i in range(self.gram_n) ]) for tokenized in tokenized_messages ]
        ngrams = [ [' '.join(ng) for ng in ngram] for ngram in ngrams ]
        ngrams = [ ngram for ngram in ngrams if len(ngram) != 0 ]

        return ngrams


    def _normalize_input(self, input: str) -> str:
        input = input.lower()

        conversion_dict = {
            'ą': 'a',
            'ć': 'c',
            'ę': 'e',
            'ł': 'l',
            'ń': 'n',
            'ó': 'o',
            'ś': 's',
            'ź': 'z',
            'ż': 'z'
        }

        for k, v in conversion_dict.items():
            input = re.sub(rf'{k}', v, input)

        input = re.sub(r'[^a-zA-Z0-9\s]', '@', input)

        return input
