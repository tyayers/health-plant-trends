import web
import requests
import json
import time
from datetime import datetime, timedelta
from google.cloud import storage, bigquery

urls = (
    '/initial(.*)', 'data_initial_load',
    '/latest(.*)', 'data_latest',
    '/growth_rates(.*)', 'data_growth'
)
app = web.application(urls, globals())


class data_growth:
    def GET(self, site):


        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json')
        
        #result = self.load(
        return json.dumps({"result": "Success"})

    def load(self, bucket, table):
        client = bigquery.Client()
        query = "SELECT * FROM `" + table + "` LIMIT 1000"
        
        query_job = client.query(query)  # Make an API request.

        result = []
        for row in query_job:
            # Row values can be accessed by field name or index.
            result.append({
                "name": row["name"],
                "date": str(row["date"]),
                "news_volume": row["news_volume"],
                "previous_news_volume": row["previous_news_volume"],
                "growth_rate": row["growth_rate"],
                "news_norm": row["news_norm"]
            })

        d = bucket.blob("output/growth_rates.json")
        d.upload_from_string(json.dumps(result))
        
        return result
        
class data_latest:
    def GET(self, site):

        storage_client = storage.Client()
        bucket = storage_client.bucket("planttrends-72642")

        terms = get_terms(bucket)
        result = get_news_volume_latest(terms)

        d = bucket.blob("inputs/news_volume_update.csv")
        d.upload_from_string(result)

        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json')
        return json.dumps({"result": "Success"})

        # web.header('Content-Type', 'text/csv')
        # return result


class data_initial_load:
    def GET(self):
        storage_client = storage.Client()
        bucket = storage_client.bucket("planttrends-72642")

        result = self.load(bucket, "sandwiches")

        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json')
        return json.dumps({"result": "Success"})

        # web.header('Content-Type', 'text/csv')
        # return result
        
    def load(self, bucket, key): 
        terms = get_terms(bucket, key)
        result = get_news_volume(terms)
        
        d = bucket.blob("input/news_volume_initial.csv")
        d.upload_from_string(result)
        
        return result

def get_terms(bucket, key):
    terms = []

    blob = bucket.blob("output/topic_entities.json")
    data = json.loads(blob.download_as_string())

    for term in data[key]:
        name = term["Name"]
        name = name.replace("-", " ")
        name_pieces = name.split(" ")
        name = ""
        for name_piece in name_pieces:
            if len(name_piece) > 2:
              name = name + " " + name_piece.replace(",", "")
            
        # name = name.replace(", ", " ").replace(" or ", "").replace(" in 
        terms.append(name)

    print(terms)

    return terms


def get_news_volume_latest(terms):
    result = ""
    yesterday_string = datetime.strftime(
        datetime.now() - timedelta(1), '%Y%m%d') + "T000000Z"
    for term in terms:
        query = ""
        queryWords = term.split(" ")
        for word in queryWords:
            tempWord = word.lower().replace(",", "").replace(".", "").replace(
                " or ", "").replace(" and ", "").replace("-", " ").replace("(", "").replace(")", "").replace("aka", "")

            if len(tempWord) > 2:
                tempWord = tempWord.replace(" ", "%20")
                
                if (query == ""):
                    query = tempWord
                else:
                    query = query + "%20" + tempWord

        url = 'https://api.gdeltproject.org/api/v2/doc/doc?query=' + \
            query + \
            '%20plant&mode=timelinevolraw&format=json&TIMESPAN=2w'
        vol = requests.get(url)

        volData = vol.json()
        if "timeline" in volData and len(volData["timeline"]) > 0:
            for day in volData["timeline"][0]["data"]:

                # Only get yesterday's value...
                if str(day["date"]) == yesterday_string:
                    if result != "":
                        result = result + "\n"

                    result = result + term.replace(",", "") + "," + day["date"] + "," + \
                        str(day["value"]) + "," + str(day["norm"])

        time.sleep(.5)

    return result


def get_news_volume(terms):
    result = ""
    for term in terms:
        query = ""
        queryWords = term.split(" ")
        for word in queryWords:
            tempWord = word.lower().replace(",", "").replace(".", "").replace(
                " or ", "").replace(" and ", "").replace("-", " ").replace("(", "").replace(")", "").replace("aka", "")

            if len(tempWord) > 2:
                tempWord = tempWord.replace(" ", "%20")
                if (query == ""):
                    query = tempWord
                else:
                    query = query + "%20" + tempWord

        print('Searching GDELT for ', query)

        url = 'https://api.gdeltproject.org/api/v2/doc/doc?query=' + \
            query + \
            '%20plant&mode=timelinevolraw&format=json'
        vol = requests.get(url)

        volData = vol.json()
        if "timeline" in volData:
        
            print('Found ', len(volData["timeline"][0]["data"]), ' records')
            for day in volData["timeline"][0]["data"]:
                if result != "":
                    result = result + "\n"

                result = result + term.replace(",", "") + "," + day["date"] + "," + \
                    str(day["value"]) + "," + str(day["norm"])

        time.sleep(.3)

    return result


if __name__ == "__main__":
    app.run()
