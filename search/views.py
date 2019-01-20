from django.shortcuts import render
import json
from django.views.generic.base import View
from search.models import ArticleType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from datetime import datetime
import redis

# elasticsearch 比 elasticsearch_dsl 更加底层的一种方法
# elasticsearch_dsl 是在其之上的各种封装 对原生方法 比较熟 可以只用 elasticsearch
client = Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis()

# Create your views here.
class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s', '')
        re_datas = []
        if key_words:
            s = ArticleType.search()
            s = s.suggest("my_suggest", key_words, completion={
                "field": "suggest",
                "fuzzy": {
                    "fuzziness": 1
                },
                "size": 10,
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source['title'])
        return HttpResponse(json.dumps(re_datas), content_type='application/json')

class SearchView(View):
    def get(self, request):
        key_words = request.GET.get('q', '')
        page = request.GET.get('p', '1')
        try:
            page = int(page)
        except:
            page = 1

        start_time = datetime.now()

        response = client.search(
            index='jobbole',
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["tags", "title", "content"]
                    }
                },
                "from": (page - 1)*10,
                "size": 10,
                # 对搜索的字段 进行高亮处理
                "highlight": {
                    "pre_tags": ['<span class="keyword">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "title": {},
                        "content": {}
                    }
                }
            }
        )

        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()


        total_nums = response["hits"]["total"]
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dist = {}
            if "title" in hit['highlight']:
                hit_dist['title'] = "".join(hit["highlight"]["title"])
            else:
                hit_dist['title'] = hit['_source']['title']
            # content 取前 500 字
            if "content" in hit['highlight']:
                hit_dist['content'] = "".join(hit["highlight"]["content"])[:500]
            else:
                hit_dist['content'] = hit['_source']['content'][:500]

            hit_dist['url'] = hit['_source']['url']
            hit_dist['score'] = hit['_score']

            hit_list.append(hit_dist)

        if(page%10) > 0:
            page_nums = int(total_nums/10) + 1
        else:
            page_nums = int(total_nums/10)


        # 将 key_words 传回去 是为了让其显示在 搜索栏
        return render(request, 'result.html', {
            "all_hits": hit_list,
            "key_words": key_words,
            "page": page,
            "total_nums": total_nums,
            "page_nums": page_nums,
            "last_seconds": last_seconds
        })


