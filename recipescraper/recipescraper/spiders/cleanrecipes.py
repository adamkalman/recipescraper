import re
import csv
import os
 
workingDirectory = "/Users/adamkalman/Desktop/recipescraper/recipescraper/recipescraper/spiders"

def replaceAll(text, dic):
    for key, value in dic.iteritems():
        text = text.replace(key, value)
    return text

def makeDict():
    stopwordsfile = open(os.path.join(workingDirectory, "stopwords.csv"),'rU')
    rd = csv.reader(stopwordsfile, delimiter = '\n')
    dic = {}
    for row in rd:
        dic[' '+row[0].strip()+' '] = '  '
    return dic

def cleanTitle(titlelist):
    str1 = titlelist[0]
    if str1[-12:] == 'Food Network':
        str2 = str1[:-15]
    else:
        str2 = str1
    match = re.search(r'Recipe : ',str2)
    if match:
        pair = str2.split(':')
        title = pair[0].strip()
        chef = pair[1].strip()
    else:
        title = str2
        chef = None
    return title, chef

def cleanIngr(ingr, dic):
    str1 = ' '+ingr+' ' #adds one whitespace char at beginning and end
    str2 = re.sub(r'[\d/\*><-]', r' ', str1) #removes all numbers, slashes, dashes, < , >, asterisks
    str3 = re.sub(r'\(.*\)',r' ',str2) #removes everything in parentheses
    str4 = re.sub(r',.+',r' ', str3) #removes everything after a comma
    str5 = re.sub(r'\sor\s.+',r' ',str4) #removes everything after the word 'or'
    str6 = str5.lower() #makes everything lowercase
    str7 = replaceAll(str6, dic) #throws out stopwords
    str8 = re.sub(r'\s\w\s',r' ',str7) #throws out stranded 's' and other single character words
    str9 = re.sub(r'\s+',r' ',str8) #turns double/triple/etc spaces into a single space
    return(str9.strip()) #strips off whitespace from beginning and end

def cleanIngs(ings):
    ingredients = []
    dic = makeDict()
    for ing in ings:
        chunks = re.findall(r'>.+?<', ing) 
        ingredient = ' '.join(chunks)
        ingredients.append(cleanIngr(ingredient, dic))
    return filter(None,list(set(ingredients)))
        
def cleanLink(link):
    if link[:5] == '<200 ':
        return unicode(link[5:-1], "utf-8") 
    elif link[0] == '/':
        return 'http://www.foodnetwork.com'+link    
    else:
        return link 