#Brian b1445249
#Project 7
#10/28/2020
#Pulling and parsing wikipedia articles
#the goal is to essentially give the user a tool to search, read and pick up wikipedia articles entirely text based
#https://www.mediawiki.org/wiki/API:Parsing_wikitext
#https://regexr.com/
#https://docs.python.org/3/tutorial/datastructures.html

#above are the resources I used


# I wanted to also make it human readible if not perfect so I had to use a bunch of regex for this
import requests #import requests as we need it to pull info from Wikipedia
import json #import JSON to parse json
import re #import Regex to make removing uneeded characters/strings easier
import io

url = "https://en.wikipedia.org/w/api.php" #setting url it's the same url so setting globally

def searchPages(searchTerm): #function to actually pull a list of wikipedia pages and return them to main
    params = "?action=query&list=search&format=json&srsearch=" + searchTerm #Parameters set plus the search term passed from main
    response = requests.get(url+params) #Actually do a get request with the whole of parameters and url
    jsonData = response.json() #convert to json
    #pretty_json = json.dumps(json.loads(response.content), indent=2)
    #print (pretty_json)
    return jsonData #return raw data

def pagePicker(inputJson, searchTerm): #Helps the user pick a valid page and verifies there are search results
    index = 0 #index for while loop
    pageTitles = {} #dictionary to store results
    while (len(inputJson['query']['search'])>index): #while the index is less than the number of records in search
        pageTitle = inputJson['query']['search'][index]['title'] #Pass index and pull the title of the page at that index
        searchTerm = searchTerm.replace("%20"," ") #replace spaces with %20 for passing to url
        pageTitle = pageTitle.lower() #lowercase the page title
        pageStatus = pageTitle.find(searchTerm) #find the search term in page title, if not there then we will continue to iterate,
        if pageStatus != -1: #check if the page was in the list
            pageTitles[pageTitle]=inputJson['query']['search'][index]['pageid'] #Keep page ID for later with a dictionary using title string as key
        index += 1 #increment index
    if len(pageTitles) == 0:
        print("There are no results for your search") #If there are no results we let the user know
        return "None"
    elif len(pageTitles) > 0: #otherwise we are going to show every title on screen and ask they pick the one they want to display
        print("There were", len(pageTitles), "results for your search. Please pick a page below to view")
        for items in pageTitles: #print off items
            print (items)
        while True: #remains true we just return out once they pick a valid option so no need to actually control this loop beyond this
            choosenTitle = input("Please Enter the above title you want to load:") #request and correct their entry
            choosenTitle = choosenTitle.lower()
            choosenTitle = choosenTitle.strip()
            if choosenTitle in pageTitles.keys():
                return (pageTitles[choosenTitle]) #return the pageid that matches the value assuming the value was in fact a key

def loadPage(pageid): #now we actually get the page

    params = "?action=parse&format=json&prop=text&prop=wikitext&pageid=" + str(pageid) #request it
    print ("Page URL:",url+params)  #print the page url incase they want it for reading graphically
    response=requests.get(url+params)
    output = response.json()
    return output

def resultShow(json):
    pageBody =json['parse']['wikitext'] #get the text
    pageTitle =json['parse']['title'] #get the title
    pageBody =str(pageBody) #Make the body a string
    pageTitle = str(pageTitle)
    pageBody = pageBody.replace(r"\n", "\n") #Replace every embedded newline with a real one
    if pageBody.startswith("{'*"): #remove starting gibberish
        pageBody = re.sub("{'\*': '","", pageBody)
        pageBody = re.sub("{{pp-semi-indef\|small=yes}}","", pageBody)
    #this is all a bunch of regex that frankly I kind of forgot what all it does but it cleans up the page.
    pageBody = re.sub("[{|}]",' ', pageBody)
    pageBody = re.sub("=", ':', pageBody)
    pageBody = re.sub("(image).*", '', pageBody)
    pageBody = re.sub("\[\[(File).*", '', pageBody)
    pageBody = re.sub("\\'", '', pageBody)
    pageBody = re.sub("\[|\]", '', pageBody)
    pageBody = (re.sub(r'\n\s*\n','\n',pageBody,re.MULTILINE))
    pageBody = re.sub("<br>", '\n', pageBody)
    pageBody = re.sub("<\/...|>|<...", ' -reference- ', pageBody)
    pageBody = re.sub("-reference-*.*", "", pageBody)
    pageBody = re.sub(r"(\\\\\\)|(\\\\)", '', pageBody)
    pageBody = re.sub("//", '', pageBody)
    pageBody = re.sub(".*.Page URL*.*",'', pageBody)
    pageBody = re.sub("redirect *.*", '', pageBody)
    pageBody = re.sub(".*.good article.*.", '', pageBody)
    pageBody = re.sub(".*pp-[a-z]*.*", '', pageBody)
    pageBody = re.sub(".*short description.*", '', pageBody)
    pageBody = re.sub(".*EngvarB.*", '', pageBody)
    pageBody = re.sub(".*Use dmy*.*",'', pageBody)
    pageBody = re.sub("Tree list/end", '}\n', pageBody)
    pageBody = re.sub("Tree list",'{\n',pageBody)
    pageBody = re.sub("align :[:\w\d\s]*total_width.*.",'', pageBody)
    pageBody = re.sub("! scope.*", '', pageBody)
    pageBody = re.sub('style:"*.*','', pageBody)
    pageBody = re.sub(".*.Number table.*.", '', pageBody)
    pageBody = re.sub("class.*.",'', pageBody)
    pageBody = re.sub("\n{3,}",'', pageBody)
    file = io.open(pageTitle+".txt", "w", encoding="utf-8") #make a file
    file.write(pageBody) #save this to a file (It's easier to read than the console)
    #weird encoding issue so I used the io module instead. https://stackoverflow.com/questions/27092833/unicodeencodeerror-charmap-codec-cant-encode-characters
    #Otherwise file writing appears to work fine, I only encountered that issue on one page, didn't bother to figure out which character caused the issue.
    return (pageBody)  # return to main



def formatString():
    searchTerm=input("Please enter an item you want to know about:") #we need to get the search
    indexLength=len(searchTerm) #Check the text and make a total to index on
    currentIndex=0 #init index
    hasLetter=False #control variable
    while True: #I just use break, not sure if it's best practice but I did that in a couple of places
        while currentIndex < indexLength: #Second loop we use it to iterate over the text
            letter=searchTerm[currentIndex] #get the current letter
            if letter.isalpha(): #check if it's alpha
                hasLetter = True
            currentIndex +=1 #increment index
        if hasLetter == True: #If there is alpha then we break
            break
        else: #Otherwise we need them to enter an actual search
            currentIndex=0
            searchTerm = input("You need at least one letter in your search term:")
    searchTerm = searchTerm.strip() #Clean up the search
    searchTerm = searchTerm.replace(" ", "%20") #make it good to use in a url
    searchTerm = searchTerm.lower() #Convert to lowercase
    return searchTerm #return it for further use

def main(): #main function
    goagain = 'yes' #control var to allow multiple searched
    #Files save as the article name so you can do multiple searches without fear of overwriting your precious stripped down text based wikipedia article
    while goagain.lower() == "yes" or goagain.startswith('y') : #while loop to keep it going
        #each of this is pretty self explanetory take one return and pass it to the next function
        searchItem = formatString()
        foundPages = searchPages(searchItem)
        pageid = pagePicker(foundPages,searchItem)
        #print (pageid)
        pageStr=str(pageid) #converting to string to use isdigit
        if pageStr.isdigit():
            content = loadPage(pageid)
            preparedText = resultShow(content)
            print(preparedText)  # print the results
            discord="https://discord.com/api/webhooks/920198172939259935/oSf-4-Pfptqa3edsyNwYk1VO1k4-Y_nLlhs2AfAWC5Dd4TQsSG2h7UVZUJCjIYRtTr-Z"
            message = {
                "content":preparedText[:1999]
                }
            requests.post(discord,message )
        goagain = input("Would you like to perform another search?")
        goagain = goagain.lower()





main()
