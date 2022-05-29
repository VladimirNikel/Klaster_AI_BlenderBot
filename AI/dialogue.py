import os
from rediscluster import RedisCluster
import json
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
from transformers import Conversation, ConversationalPipeline
from typing import Tuple, Any

blenderbot = {
    '90m': 'facebook/blenderbot-90M',
    '400m': 'facebook/blenderbot-400M-distill',
    '1b': 'facebook/blenderbot-1B-distill',
    '3b': 'facebook/blenderbot-3B'
}
model_name = blenderbot.get(os.getenv("MODEL", "400m"))
model = BlenderbotForConditionalGeneration.from_pretrained(model_name)
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)

redis_connect = json.loads(os.getenv('REDIS_CONNECT', ''))
startup_nodes = redis_connect.get('hosts')
password = redis_connect.get('password')
redis_db = RedisCluster(startup_nodes=startup_nodes, password=password, decode_responses=True)


async def list_segmentation(input_list) -> list:
    delimiter = ['bot', 'user']
    output_list = []
    for item in input_list:
        if item in delimiter:
            output_list.append([])
        output_list[-1].append(item)
    return output_list


async def init_new_dialogue(user_id: str) -> Tuple[Any, Any]:
    from_memory = await list_segmentation(redis_db.lrange(user_id, 0, -1))
    print(from_memory)
    conversation = Conversation()
    for index, message in enumerate(from_memory):
        print(message)
        if not message:
            continue
        if message[0] == 'bot':
            conversation.append_response(response=message[1])
        else:
            conversation.add_user_input(text=message[1])
            if not index+1 == len(from_memory):
                conversation.mark_processed()

    return conversation, ConversationalPipeline(model=model, tokenizer=tokenizer)
