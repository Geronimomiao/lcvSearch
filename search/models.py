from django.db import models

# Create your models here.
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, Completion, Keyword, Text, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

connections.create_connection(hosts=["localhost"])

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}
k_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

class ArticleType(DocType):
    # 伯乐在线文章类型

    # 开启智能提示 功能
    suggest = Completion()

    title = Text(analyzer="ik_max_word")
    url = Keyword()
    url_object_id = Keyword()
    praise_nums = Integer()
    fav_nums = Integer()
    comment_nums = Integer()
    tags = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    front_image_url = Keyword()
    front_image_path = Keyword()

    class Meta:
        index = 'jobbole'
        doc_type = "article"

if __name__ == '__main__':
    ArticleType.init()