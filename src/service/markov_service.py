import random
import re
from nextcord import TextChannel, Object

from model.exception.channel_not_learned import ChannelNotLearned
from model.markov.markov_grammar import MarkovGrammar


class MarkovService:
    '''Class responsible for operating the Markov Chain model.'''
    def __init__(self) -> None:
        self.grammars: dict[int, MarkovGrammar] = {}
        self.sentence_starts: dict[int, list[str]] = {}
        self.newest_message: dict[int, int] = {}
        self.gram_n = 2
        self.max_message_length = 500

    async def learn(self, channel: TextChannel) -> bool:
        '''Learns the model for a specified channel. Returns bool value indicating success or failure.'''

        if channel.id in self.newest_message:
            messages = [ msg async for msg in channel.history(oldest_first=False, limit=None, after=Object(self.newest_message[channel.id])) ]
        
        else:
            messages = [ msg async for msg in channel.history(oldest_first=False, limit=None) ]
        
        if len(messages) == 0:
            raise Exception

        messages_content = [ msg.content for msg in messages ]

        self.newest_message[channel.id] = messages[0].id

        # 1. filter messages - command invokations, hyperlinks, mentions etc
        # 1.1 remove hyperlinks
        messages_content = [ re.sub(r'(?:https?|ftp)\:\/\/.*?(?:$|\s)', '', msg)      for msg in messages_content ]

        # 1.2 remove command invokations, mentions, tags etc
        messages_content = [ re.sub(r'(?:^|\s)[!<$%^&*\-\+=\?\/\.\,][^\s]+', '', msg) for msg in messages_content ]
        
        # 2. tokenize messages
        tokenized_messages = [ [ m for m in msg.split(' ') if m != '' ] for msg in messages_content ]
        
        # 2.1. generate n-grams
        ngrams = [ zip(*[ tokenized[i:] for i in range(self.gram_n) ]) for tokenized in tokenized_messages ]
        ngrams = [ [' '.join(ng) for ng in ngram] for ngram in ngrams ]
        ngrams = [ ngram for ngram in ngrams if len(ngram) != 0 ]
        
        # 3. create and save grammar
        if channel.id not in self.grammars:
            self.grammars[channel.id] = MarkovGrammar()
            self.sentence_starts[channel.id] = []
        
        for n in ngrams:
            for m in n:
                splitted = m.split(' ')

                input = ' '.join(splitted[:-1])
                
                # normalize input
                input = self._normalize_input(input)

                output = m

                self.grammars[channel.id] += [input, output]

        # 4. save sentence start
        for n in ngrams:
            splitted_first_ngram = n[0].split(' ')

            self.sentence_starts[channel.id].append(' '.join(splitted_first_ngram[:-1]))
        
        # 5. verify
        # self.grammars[channel.id].print_matrixes()
        # print(self.sentence_starts[channel.id])
    
    async def say(self, channel: TextChannel) -> str:
        if channel.id not in self.grammars:
            raise ChannelNotLearned

        # choose a starting ngram
        starting = random.choice(self.sentence_starts[channel.id])

        # generate a poem
        generated_message = starting

        try:
            while len(generated_message) < self.max_message_length:
                input = ' '.join(generated_message.split(' ')[1 - self.gram_n:])
                
                # normalize input
                input = self._normalize_input(input)
                
                output = self.grammars[channel.id][input]

                generated_message = f'{" ".join(generated_message.split(" ")[:1 - self.gram_n])} {output}'
        
        finally:
            return generated_message
    
    def _normalize_input(self, input: str) -> str:
        input = re.sub(r'[^a-zA-Z0-9\s]', ' ', input)

        return input


markov_service = MarkovService()
