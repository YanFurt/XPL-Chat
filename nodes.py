from classes import State,Group,Filters
import json
from prompts import *
from langchain.chat_models import init_chat_model
from tools import human_assistance

llm = init_chat_model("google_genai:gemini-2.5-flash")
filter_llm=llm.bind_tools([human_assistance])#.with_structured_output(Filters)
field_llm=llm.with_structured_output(Group)


def get_collections(state: State):
    p=collection_prompt.invoke({'question':state['userquery']})
    output=llm.invoke(p)
    #print(output)
    return {"collection":output.content}

def get_filters(state:State):
    #print(state)
    if state['messages']:
        exp = ' '+state['messages'][-1].content
    else:
        exp=''
    p=filter_prompt.invoke({'question':state['userquery']+exp,'match_info':match_lookup[state['collection']]})
    
    output=filter_llm.invoke(p)
    #print(output)
    if tc := output.tool_calls:
        return {'messages':[output]}
    
    output=Filters.model_validate(json.loads(output.content))
    
    return {"matches":output.Match,'teams':output.Team,'userquery':state['userquery']+exp}

def get_fields(state:State):
    p=fields_prompt.invoke({'question':state['userquery']})
    output=field_llm.invoke(p)
    return {"fields":output.fields,'operator':output.operator}

def get_agg(state:State):
    p=type_prompt.invoke({'question':state['userquery'],"match data":match_lookup2[state['collection']]})
    return {"agg": llm.invoke(p).content}
    
def get_query(state: State):
    p=mongo_prompt.invoke({'question':state['userquery']})
    output=llm.invoke(p)
    #print(output)
    return {"mongoExp": output}

def get_response(state: State):
    if state['collection']:
        p=summary_prompt.invoke({'data':state['data'],'question':state['userquery']})
        #print(p)
        return {"response": llm.invoke(p).content}
    else:
        return {"response":"I can only answer questions about XPL 2025"}

def dummy_node(state:State):
    return {}


#@tool
#def fetch_data(collections: Annotated[List[str], 'List of collections to be queried'],expression:MongoQuery)->Any:
def fetch_data(state:State, config):
    "To query the given collections MongoDB database and return the output for the aggregation pipeline defined by the provided expression"
    database=config["configurable"]["database"]
    data={}
    pipe=[]
    match_stage=[]
    if match:=state['matches']:
        match_stage.append({'Match':{'$in':match}})
    else:
        match_stage.append({'Match':{'$not':{'$eq':'Unsold'}}})
    if teams := state['teams']:
        match_stage.append({'Team':{'$in':teams}})
    else:
        match_stage.append({'Team':{'$nin':['Unsold']}})
    
    pipe.append({"$match":{'$and':match_stage}})

        
    fields=state['fields']
    group_stage={'$group':{'_id':"$Team",**{i:{state['operator']:f'${i}'} for i in fields}}}
    pipe.append(group_stage)
    dct = {i:1 for i in fields}
    dct['_id']=0
    dct['Team']='$_id'
    pipe.append({"$project":dct})
    print(pipe)
    data=database[state['collection']].aggregate(pipe).to_list()
    return {'data':data}
    
def route1(state:State):
    if state['collection'].lower()=='not applicable':
        return 'get_response'
    else:
        return 'dummy_node1'