from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from boards.serializer import BoardFilesSerializer, BoardSerializer
from .models import Board, FileBoard
from .patterns import school_daechi, school_dorim
from rest_framework import generics


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class BoardListView(generics.ListAPIView):
    pagination_class = StandardResultsSetPagination
    queryset = Board.objects.all()
    serializer_class = BoardSerializer


class BoardView(APIView):

    # def get(self, request):
    #     """
    #     view data
    #     :param request:
    #     :return: select category & schools
    #     """
    #     # Board.objects.filter(school_name=school_name).select_related()
    #     school_name = request.GET['schoolName']
    #     category = request.GET['category']
    #     query = Board.objects.filter(school_name=school_name, category=category).values()
    #     return Response(data=query)

    def get(self, request):
        """
        update board data
        :param request:
        :return: update status
        """
        # school_name = request.GET['school_name']
        # if school_name == '대치초등학교':
        #     if school_daechi.Crawling().school_crawler():
        #         return Response(data={"data": "Update", "status": True}, status=status.HTTP_201_CREATED)
        #     return Response(data={"data": "Update", "status": False}, status=status.HTTP_204_NO_CONTENT)
        # elif school_name == '도림초등학교':
        #     if school_dorim.Crawling().school_crawler():
        #         return Response(data={"data": "Update", "status": True}, status=status.HTTP_201_CREATED)
        #     return Response(data={"data": "Update", "status": False}, status=status.HTTP_204_NO_CONTENT)
        # return Response(data={"data": "no content"}, status=status.HTTP_400_BAD_REQUEST)
        if school_dorim.Crawling().school_crawler() or school_daechi.Crawling().school_crawler():
            return Response(data={"result": "Success", "status": True}, status=status.HTTP_201_CREATED)
        return Response(data={"result": "no Data Update", "status": False}, status=status.HTTP_202_ACCEPTED)


class BoardFiles(APIView):
    def get(self, request):
        """
        :param request:
        :return: file url data
        """
        post_id = request.GET['id']
        query = FileBoard.objects.filter(post__id=post_id)
        serializer = BoardFilesSerializer(query, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
