from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
match_lookup={'League_Games':'Each document in the collection has a field "Match" which has the Match to which the document pertains. It has values like "Match 1", "Match 2" ... upto "Match 70".',
             'Knockout_Games':'Each document in the collection has a field "Match" which has the Match to which the document pertains. It has values like "Eliminator", "Qualifier 1" and "Qualifier 2".',
             'Overall_Season':"Each document in the collection contains aggregated stats of the player over the whole season"}

match_lookup2={'League_Games':'The matches have names like  "Match 1", "Match 2" ... upto "Match 70".',
             'Knockout_Games':'The matches have names "Eliminator", "Qualifier 1" and "Qualifier 2".'}

collection_prompt_template='''You are MongoDB database manager. You will get queries to fetch cricket stats for the completed fantasy IPL league and have to figure out which tables to query to fetch the required data.
The fantasy league had 7 teams. Each team had 20 players from the 8 IPL franchises.

The 7 fantasy teams are:
-Yannick's Fireballs: Saved as "Yannick" in the database
-Nihaar's Trailblazers: Saved as "Nihaar" in the database
-Jinto's Merciless Strikers: Saved as "Jinto" in the database
-Vatsal's Invincibles: Saved as "Vatsal" in the database
-Yatharth's Nawabi Knight Riders: Saved as "Yatharth" in the database
-Swatantra's Spartan Warriors: Saved as "Swatantra" in the database
-Sayak's Storm Troopers: Saved as "Sayak" in the database

The tables in the database are:

-Collection name: Knockout_Games
 Collection description: Contains match-wise stats for each player in the playoffs games. The playoff games are: "Eliminator", "Qualifier 1" and "Qualifier 2".

-Collection name: League_Games
 Collection description: Contains match-wise stats for each player in each league game of the season. The league matches include "Match 1", "Match 2" ... upto "Match 70"

-Collection name: Overall_Season
 Collection description: Contains summarized stats over the season for each player.

Instructions:
-Output only the name of the collection needed to answer the query:
-If the question is asked about something other than the fantasy league, output  "Not applicable"

Examples:

Q: What were Yannick's combined stats in Match 10 and 11.
A: League_Games

Q: How many runs did the Storm Troopers score in the season
A: Overall_Season

Q: How many wickets were taken by the top 4 teams
A: Overall_Season

Q: Did Tom take 50 wickets 
A: Overall_Season

Q: How many teams scored more points from wickets than from runs in the playoffs
A: Knockout_Games

Q: Between Swatantra and Nihaar, who had more points in the last 5 league matches?
A: League_Games

Q: Which team scored the most points in the playoffs?
A: Knockout_Games

Q: What is your name?
A: Not applicable

Q: {question}
A: '''

collection_prompt=PromptTemplate.from_template(collection_prompt_template)


filter_prompt_template='''You are MongoDB database manager. You will get questions about cricket stats for the completed fantasy IPL league and have to figure out which filters to apply to the collection to fetch the required data to answer the query. You will be a given a list of the fields on which filters can be applied and a list of the 7 teams participating in the fantasy league.

The 7 fantasy teams are:
    -Yannick's Fireballs: Saved as "Yannick" in the database
    -Nihaar's Trailblazers: Saved as "Nihaar" in the database
    -Jinto's Merciless Strikers: Saved as "Jinto" in the database
    -Vatsal's Invincibles: Saved as "Vatsal" in the database
    -Yatharth's Nawabi Knight Riders: Saved as "Yatharth" in the database
    -Swatantra's Spartan Warriors: Saved as "Swatantra" in the database
    -Sayak's Storm Troopers: Saved as "Sayak" in the database

Metadata:
    -Each document in the collection has a field "Team" which has the name of the fantasy team that the player belongs to
    -{match_info}

Instructions:
-Output an object containing the filters on "Match" or "Team" fields,  needed to answer the query.
-The Output should be a json object with only the keys "Match", "Team".
-Do not use any backticks or the word 'json' in your output.
-The values in the output json should be a list of values which the collection needs to be filtered on.
-If match or team is not specified then output an empty list for "Match" or "Team"
-For teams, only use the first word of the franchise name
-If you cannot identify the team or match whose information is being queried, request ask the user about your doubt before proceeding by using the 'human_assistance' tool

Examples:

Q: What were Yannick's combined stats in Match 10 and 11
A: {{"Match":["Match 10","Match 11"], "Team":["Yannick"] }}

Q: How many runs did the Storm Troopers score in the season
A: {{"Team":["Sayak"]}}

Q: How many wickets were taken by the top 4 teams
A: {{"Match":[], "Team":[]}}

Q: How many teams scored more points from wickets than from runs in the Eliminator.
A: {{"Match":["Match 23"]}}

Q: Which team was leading after the first 5 league matches.
A: {{"Match":["Match 1", "Match 2", "Match 3", "Match 4", "Match 5"]}}

Q: {question}
A: '''

filter_prompt=PromptTemplate.from_template(filter_prompt_template)


fields_template='''You are a data analyst working on MongoDB databases. You use the pymongo client library.
You will be given a human query, and a list of fields available in the MongoDB collection which need to be queried to resolve it.
You need to decide which fields are needed to answer the query and which aggregation operation needs to be applied on them.

The fields or stats available to query are:
    -Under batting stats:
        --Runs : Points for Runs scored
        --Fours: Points for hitting fours
        --SR: Points for strike 
        --Sixes: Sixes hit by the Team
        --Thirty: Points for scoring 30+
        --Fifty: Points for scoring 50+ or a half-century
        --Hundred: Points for scoring a century or 100+

    -Under bowling stats:
        --Wickets: Wickets taken by the team
        --ER: Points for economy rate
        --Three_W: Points for taking 3+ wickets
        --Four_W: Points for taking 4+ wickets
        --Five_W: Points for taking 5+ wickets
        --Dots: Dots bowled by the team.
        --Maidens: Points for bowling maidens.

    -Under fielding stats:
        --Catches: Points for Catches taken 
        --Runout: Points for effecting a runout
        --Direct_Runout: Points for effecting a direct runout
        --Stumping: Points for effecting a stumping
    
  
    -Miscellaneous points:
        --Appearance : Points for appearances
        --Total: Total points

Available operators:
    -$sum: When total points are asked, or when aggregation is not specified
    -$avg: When average metric is asked
    -$max: When highest value of a metric or stat is asked team-wise
    -$min: When lowest value or a metric or stat is asked
    

Instructions:
-Output an object of queries which have to be run against each Collection, with the following schema.
{{"fields": <List of fields>, "operator": <operation to be applied>}} 
-Ensure you output an object with field and operator as keys
-If you are not sure about the operator, use $sum



Examples:

Q: What were Yannick's combined stats in Match 10 and 11
A: {{"fields":["Runs","Wickets","Catches","Dots","Sixes"],"operator":"$sum" }}

Q: What is the highest number of catches taken in any match team-wise
A: {{"fields":["Catches"],"operator":"$max"}}

Q: How many fielding points were scored by Yannick in the playoffs.
A: {{"fields":["Catches","Runout","Direct_Runout","Stumping"],"operator":"$sum"}}

Q: Which was the highest scoring team in the eliminator in terms of runs and wickets.
A: {{"fields":["Runs","Wickets"],"operator":"$sum"}}

Q: Which team has the highest average dots
A: {{"fields":["Dots"], "operator":"$avg"}}

Q: {question}
A: '''

fields_prompt=PromptTemplate.from_template(fields_template)


mongo_template='''You are a data analyst working on MongoDB databases. You use the pymongo client library.
You will be given a human query, and a list of collections in MongoDB which need to be queried to resolve it.
For each collection, output the expressions for the $match, $group , $sort and $limit stages of the aggregation pipeline in mongodb.

Instructions:
-Output an object of queries which have to be run against each Collection, with the following schema.
{{"group": <group expression as a dictionary>, sort: <object with keys as fields and values as sort order>}} 
-The sort stage is Optional and only needed if the query asks for a ranking like with the worst top, bottom , best, worst, highest, lowest
-The "_id" attribute of group key should always have the value $Team, or null if Team-wise data is not requested.
-the key is the sort object should have value 1 for ascending order and -1 for descending order.
-Ensure you output and object with group and sort as keys

The fields or stats available to query are:
-Runs : Runs scored by the team
-Wickets: Wickets taken by the team
-Catches: Catches taken by the team
-Sixes: Sixes hit by the Team
-Dots: Dots bowled by the team
-Total: Total Points scored by the team

Other sources of points are:
-Appearance : Points for appearances
-ER: Points for economy rate
-SR: Points for strike rate
-Thirty: Points for scoring 30+
-Fifty: Points for scoring 50+ or a half-century
-Hundred: Points for scoring a century or 100+

Examples:

Q: What were Yannick's combined stats in Match 10 and 11
A: {{"group":{{"_id":"$Team" ,"Runs":{{"$sum":"$Runs"}},"Wickets":{{"$sum":"$Wickets"}},"Catches":{{"$sum":"$Catches"}},"Dots":{{"$sum":"$Dots"}},"Sixes":{{"$sum":"$Sixes"}}}}}}}}

Q: How many runs did the Storm Troopers score in the season
A: {{"group":{{"_id":"$Team" ,"Runs":{{"$sum":"$Runs"}}}}}}

Q: How many wickets were taken by the top 4 teams
A: {{"group":{{"_id":"$Team" ,"Wickets":{{"$sum":"$Wickets"}}}}}},"sort":"{{"Runs":-1}}}}}}}}

Q: How many teams scored more points from wickets than from runs in match 23
A: {{"group":{{"_id":"$Team" ,"Runs":{{"$sum":"$Runs"}},"Wickets":{{"$sum":"$Wickets"}}}}

Q: Which team was leading after the first 5 matches
A: {{"group":{{"_id":"$Team" ,"Total":{{"$sum":"$Total"}}}},"sort":{{"Total":-1}}}}

Q: {question}
A: '''

mongo_prompt=PromptTemplate.from_template(mongo_template)

type_temp='''You are a data analyst working with mongodb. you need to answer a user query using one or more collections from the database.
The collections contains data pertaining to a cricket tournament and each document contains stats of a player in a particular match.
Each document has the field 'Match' which mentions the match pertaining the document, and a field 'Team' stating which Team the player belongs to. 
You will be asked a question based on the collection and need to decide whether the given query needs to aggregate data at a match level, or at a team level.
You will already receive filtered data and only need to decide the aggregation.

Context:
The 7 fantasy teams are:
-Yannick's Fireballs: Saved as "Yannick" in the database
-Nihaar's Trailblazers: Saved as "Nihaar" in the database
-Jinto's Merciless Strikers: Saved as "Jinto" in the database
-Vatsal's Invincibles: Saved as "Vatsal" in the database
-Yatharth's Nawabi Knight Riders: Saved as "Yatharth" in the database
-Swatantra's Spartan Warriors: Saved as "Swatantra" in the database
-Sayak's Storm Troopers: Saved as "Sayak" in the database

The matches are:
{match_data}


Instructions:
-If we need to aggregate data at a match level, output "Match".
-If we need to aggregate data at a team level, output "Team".
-Usually, if we are asked to compare stats of 2 or more teams, or rank teams we need to aggregate at a team level.
-If asked to compare stats between matches, then we need to aggregate at a match level
-If we are asked for total or combined numbers across matches, then no aggregation is needed for Match


Examples:

Q: What were Yannick's combined stats in Match 10 and 11
A: Team

Q: How many runs did the Storm Troopers score in the season
A: Team

Q: In which match did Vatsal take the most wickets
A: Match

Q: In which match did Jinto score the highest number of points.
A: Match

Q: Which team was leading after the first 5 matches
A: Team

Q: Who were the leading points scorers in the last 3 matches respectively
A: Match

Q: {question}
A:'''

type_prompt=PromptTemplate.from_template(type_temp)

summary_template="""You are a data analyst who needs to summarize the given data to answer the given question.
You will be given a human query, and some numerical data in json format to use to answer it.

Instructions:
-Output a single summary that answers the query. Provide some numbers and metrics.
-Assume that the data satisfies the filters in the query

Question:
{question}

Data:
{data}"""

summary_prompt=PromptTemplate.from_template(summary_template)