from socket import timeout
from django.shortcuts import render, redirect
import requests
from rest_framework.authtoken.models import Token
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout

def get_url(request):
    return request.scheme + "://" + request.get_host()

def team_page(request):
    try:
        token = Token.objects.get_or_create(user=request.user)[0].key
        headers = {"Authorization":"Token "+ token}
    except:
        headers = {"Authorization":None}

    context = {}
    url = get_url(request) + "/api/v1/team_page"
    r = requests.get(url = url, headers=headers, timeout=10)
    if(r.status_code == 200):
        context['team'] = r.json()
    else:
        context['error'] = r.content.decode("utf-8")
    
    if request.method == "POST":
        url = get_url(request) + "/api/v1/transfer_player/" + request.POST.get("transfer-btn") +"/"
        print(url)
        data = {
            "asking_price":  request.POST.get("asking-price"),
        }
        r = requests.patch(url = url, data = data, headers = headers, timeout=10)
        if(r.status_code == 200):
            context['message'] = "Transfer Successful"
            return redirect('team_page')

        else:
            context['message'] = r.content.decode("utf-8")

    return render(request, "team_page.html", context)

def transfer_list(request):
    try:
        token = Token.objects.get_or_create(user=request.user)[0].key
        headers = {"Authorization":"Token "+ token}
    except:
        headers = {"Authorization":None}

    context = {}
    url = get_url(request) + "/api/v1/transfer_list"
    r = requests.get(url = url, headers=headers, timeout=10)
    if(r.status_code == 200):
        context['transfer_list'] = r.json()
    else:
        context['message'] = r.content.decode("utf-8")
    
    if request.method == "POST":
        url = get_url(request) + "/api/v1/purchase_player/" + request.POST.get("buy-btn") +"/"
        r = requests.patch(url = url, headers = headers, timeout=10)
        if(r.status_code == 200):
            context['message'] = "Purchase Successful"
            return redirect('transfer_list')

        else:
            context['message'] = r.content.decode("utf-8")

    return render(request, "transfer_list.html", context)