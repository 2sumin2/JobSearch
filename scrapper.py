import requests
from bs4 import BeautifulSoup

def so_get_last_page(url):
  result = requests.get(url)
  soup = BeautifulSoup(result.text,"html.parser")
  pages = soup.find("div", {"class":"s-pagination"}).find_all("a")
  last_page = pages[-2].get_text(strip=True)
  return int(last_page)

def so_extract_job(html):
  title = html.find("h2").find("a")["title"]
  company, location = html.find("h3").find_all("span", recursive=False)
  company = company.get_text(strip=True)
  location = location.get_text(strip=True).strip("-").strip("\r").strip("\n")
  job_id = html['data-jobid']
  return {
    'title':title,
    'company':company,
    'location':location,
    "apply_link":f"https://stackoverflow.com/jobs/{job_id}"
  }
  
def wwr_extract_job(html):
  company = html.find("span",{"class", "company"}).get_text(strip=True)
  title = html.find("span",{"class", "title"}).get_text(strip=True)
  location = html.find("span",{"class", "region"}).get_text(strip=True)
  href = html.find_all("a")
  link = f"https://weworkremotely.com/{href[1]['href']}"
  return {
    'title':title,
    'company':company,
    'location':location,
    "apply_link":link
  }

def re_extract_job(html):
  html = html.find("td",{"class", "company"})
  company = html.find("h3").get_text(strip=True)
  title = html.find("h2").get_text(strip=True)
  location = html.find("div",{"class", "location"}).get_text(strip=True)
  href = html.find("a")['href']
  link = f"https://remoteok.com/{href}"
  return {
    'title':title,
    'company':company,
    'location':location,
    "apply_link":link
  }

def so_extract_jobs(last_page, url):
  jobs=[]
  for page in range(last_page):
    print(f"Scrapping SO: Page: {page}")
    result = requests.get(f"{url}&pg={page+1}")
    soup = BeautifulSoup(result.text, "html.parser")
    results = soup.find_all("div", {"class":"-job"})
    for result in results:
      job = so_extract_job(result)
      jobs.append(job)
  return jobs

def wwr_extract_jobs(url):
  jobs=[]
  print(f"Scrapping WWR")
  result = requests.get(url)
  soup = BeautifulSoup(result.text, "html.parser")
  results = soup.find_all("li", {"class":"feature"})
  for result in results:
    job = wwr_extract_job(result)
    jobs.append(job)
  return jobs

def re_extract_jobs(url):
  jobs=[]
  print(f"Scrapping RO")
  result = requests.get(url)
  soup = BeautifulSoup(result.text, "html.parser")
  results = soup.find_all("tr", {"class":"job"})
  for result in results:
    job = re_extract_job(result)
    jobs.append(job)
  return jobs

def get_jobs(word):
  #stackoverflow
  so_url = f"https://stackoverflow.com/jobs?q={word}&sort=i"
  so_last_page = so_get_last_page(so_url)
  jobs= so_extract_jobs(so_last_page, so_url)

  #wwr
  wwr_url = f"https://weworkremotely.com/remote-jobs/search?utf8=%E2%9C%93&term={word}"
  jobs= jobs + wwr_extract_jobs(wwr_url)

  #remoteok
  re_url = f"https://remoteok.com/remote-{word}-jobs"
  jobs= jobs + re_extract_jobs(re_url)
  
  return jobs