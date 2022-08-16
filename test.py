import requests
key = "ibnAs5jIisuvDfjezzvc7SE4XzdTAdRPxnOUJnMhgygjM%2BOFK5jVQVu2iGXWEvk3EwhtKqIXWbjHtv%2FZd75KtA%3D%3D"
url = 'http://apis.data.go.kr/6460000/tourCourse/getTourCourseList'
params ={'serviceKey' : f'{key}', 'tourCategory' : '봄', 'pageSize' : '10', 'startPage' : '1', 'numOfRows' : '10' }

response = requests.get(url, params=params)
print(response.content)
