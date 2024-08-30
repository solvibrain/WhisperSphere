from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer
@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    # here RoomSerializer takes one objects but here we are passing list of objects therefore we need to keep many = True
    serializer = RoomSerializer(rooms,many=True)
    return Response(serializer.data)



@api_view(['GET'])
def getSingleRoom(request,pk):
    room = Room.objects.get(id=pk)
    # Taking one Object and returning information about that object through api
    serializer = RoomSerializer(room,many=False)
    return Response(serializer.data)


    