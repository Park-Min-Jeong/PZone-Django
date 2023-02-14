from django.shortcuts import render
from apps.utils import connectDB

def index(request):
    if request.user.is_authenticated:
       sql = f"SELECT av_score FROM score WHERE username = '{request.user.username}'"
       row = connectDB(sql)
       if row:
           print(row)
           context = {"av_score": int(row[0][0])}
           return render(request, 'home.html', context)
       else:
           sql=f"INSERT INTO `score` (`username`, `av_score`) VALUES ('{request.user.username}', '5.0');"
           connectDB(sql, foo=True)
           sql = f"SELECT av_score FROM score WHERE username = '{request.user.username}'"
           row = connectDB(sql)
           print(row)
           context = {"av_score": int(row[0][0])}
           return render(request, 'home.html', context)
    else:
        context={}
        return render(request, 'home.html', context)

