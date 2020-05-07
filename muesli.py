from requests_html import HTMLSession
from bs4 import BeautifulSoup
from tabulate import tabulate
import os

#possibility 1: create passwords.py file with function mueslipayload() returning {'email': 'aa000@stud.uni-heidelberg.de', 'password': 'sehrsicherespasswort'}
import passwords
payload = passwords.mueslipayload()

#possibilty 2: just do it in this document
#payload = {'email': 'aa000@stud.uni-heidelberg.de', 'password': 'sehrsicherespasswort'}


url = 'https://muesli.mathi.uni-heidelberg.de/user/login'

s = HTMLSession()
result = s.post(
	url,
	data = payload, 
	headers = dict(referer=url)
)

soup = BeautifulSoup(result.text, "html.parser")

alist = soup.find_all("a")

lectures = []

for a in alist:
    if "lecture/view_points" in a["href"] and "https" in a["href"]:
            lecture = {}
            lecture["link"] = a["href"]
            lecture["name"] = a.text.split("(")[0][:-1]
            lecture["tutor"] = a.text.split("(")[1].split(",")[1][1:]
            lecture["time"] = a.text.split("(")[1].split(",")[0]
            lectures.append(lecture)


for lecture in lectures:
    lectureresult = s.get(lecture["link"])
    lectureresult.html.render(send_cookies_session=True)
    soup = BeautifulSoup(lectureresult.html.html, "html.parser")
    data = []
    resultsexist = True
    table = soup.find('table')
    
    if table:
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = []
            cols.append(''.join(row.find('th').text.split()))
            results = row.find_all('td')
            for result in results:
                cols.append(''.join(result.text.split()))
            data.append(cols)
    
    lecture["results"] = data

for lecture in lectures:
    lecture["tex"] = tabulate(lecture["results"], tablefmt="latex")

lines = [r"\documentclass{article}", r"\usepackage[ngerman]{babel}", r"\usepackage[T1]{fontenc}",  r"\begin{document}"]

for lecture in lectures:
    lines.append(r"\section{" + lecture["name"] + r"}")
    lines.append(lecture["tex"])

lines.append(r"\end{document}")

with open("results.tex", "w") as f:
    f.writelines("%s\n" % line for line in lines)

os.system("pdflatex results.tex")