from flask import Flask, Response
import redis
import requests
import urllib
from flask import request

app = Flask(__name__)
redis_store = redis.StrictRedis(host='localhost', port=6233, db=0)


@app.route("/query/", methods=['POST'])
def index():
    url = request.form['url']
    text = ""

    if not redis_store.exists(url):
        word_urlencoded = urllib.quote_plus(url.encode("utf8"))
        text = url
        redis_store.set(url, text)
    else:
        text = redis_store.get(url)

    redis_store.incr(url + ":count")

    headers = {"Cache-Control": "max-age=%d" % (3600 * 24 * 7,)}
    return Response(response=text,
                    status=200,
                    mimetype="application/xml",
                    headers=headers)


@app.route("/list/")
def url_list():
    keys = sorted(redis_store.keys())
    html = "<pre>" + "\n".join(keys)
    html += "\n\nTotal: {}".format(len(keys)) + "</pre>"
    return html


@app.route("/count/")
def request_count():
    keys = redis_store.keys(pattern="*:count")
    results = [{"key": key[:-6], "value": redis_store.get(key)} for key in keys]
    results = sorted(results, key=lambda r: int(r["value"]), reverse=True)

    formated_results = ["{:>8}  {}".format(result["value"], result["key"]) for result in results]
    html = "<pre>" + "\n".join(formated_results)
    html += "\n\nTotal: {}".format(len(keys)) + "</pre>"

    return html


if __name__ == "__main__":
    app.debug = True
    app.run()
