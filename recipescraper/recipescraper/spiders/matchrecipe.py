import re
import csv
import os
import pandas as pd
import cleanrecipes as cr
import collections
import matplotlib.pyplot as plt
import nltk

workingDirectory = "/Users/adamkalman/Desktop/recipescraper/recipescraper"
datafile = "recipedata.csv"
chefname = ''

def barhFromList(mylist, xlabel='Frequency', title='', saveas='', top=None, freqrelto=None):
    freqdict = collections.Counter(mylist)
    if freqrelto:
        for key in freqdict.keys():
            freqdict[key] = float(100*freqdict[key])/freqrelto
    freqSeries = pd.Series(freqdict, index=sorted(freqdict.keys(), key=lambda x: freqdict[x]))
    freqSeries.to_csv(os.path.join(workingDirectory, "recipescraper/spiders/topingrs.csv"), encoding='utf-8')
    if top:
        freqSeries = freqSeries[-top:]
    fig = plt.figure()
    freqSeries.plot(kind='barh',color='k',alpha=0.7)
    plt.xlabel(xlabel, fontsize=18)
    fig.suptitle(title, fontsize=20)
    plt.subplots_adjust(left=0.25, right=0.9, top=0.9, bottom=0.1)
    #plt.show() #program seems to be crashing on this line, so I'm commenting it out
    if saveas:
        fig.savefig(saveas)
    plt.close('all')
    
def main():    
    pantryfile = open(os.path.join(workingDirectory, "recipescraper/spiders/pantry.csv"),'rU')
    rd = csv.reader(pantryfile, dialect=csv.excel_tab, delimiter = '\n')
    pantry = []
    for row in rd:
        pantry.append(row[0])
    onhandfile = open(os.path.join(workingDirectory, "recipescraper/spiders/onhand.csv"),'rU')
    rd = csv.reader(onhandfile, dialect=csv.excel_tab, delimiter = '\n')
    onhand = []
    for row in rd:
        onhand.append(row[0])
    
    if chefname:
        instext = chefname
    else:
        instext = 'Food Network'   
    print 'What would '+instext+' make, using a standard pantry, plus',
    for item in onhand[:-1]:
        print item+',',
    print onhand[-1]+'.'
    onhand = list(set(pantry+onhand))
    
    recipeFrame = pd.read_csv(os.path.join(workingDirectory, datafile))
    recipeFrame.columns = ['title','url','chef','ingredients']
    recipeFrame['numMissing'] = 0
    missingIngrLists = []
    hugeingslist = []
    
    print 'Finished reading', len(recipeFrame), 'recipes into recipeFrame...'
    
    if chefname:
        recipeFrame = recipeFrame[recipeFrame.chef == chefname].reset_index(drop=True)
    
    dic = cr.makeDict()
    numMiss = []
    pctMiss = []
    for index, row in recipeFrame.iterrows(): 
        ingslist = eval(row['ingredients'])
        cleanIngslist = []
        for ing in ingslist:
            cleanIngslist.append(ing) #cleanIngslist.append(cr.cleanIngr(ing,dic))
            hugeingslist.append(ing)
        missingIngrLists.append(cleanIngslist)
        for ingr in onhand:
            ingredient = cr.cleanIngr(ingr, dic)
            if ingredient in missingIngrLists[index]:
                missingIngrLists[index].remove(ingredient) 
        numMiss.append(len(missingIngrLists[index]))
        pctMiss.append(round(100*len(missingIngrLists[index])/(0.0001+len(ingslist)),2))
        
    recipeFrame['missingIngrs'] = missingIngrLists
    recipeFrame['numMissing'] = numMiss
    recipeFrame['pctMissing'] = pctMiss
    
    print 'Finished adding new columns numMissing, pctMissing, missingIngrs to recipeFrame...'
    
    #compare missingIngrs to title. If any are included, change pctMissing to 100%
    porter = nltk.stem.porter.PorterStemmer() ##
    for index, row in recipeFrame.iterrows():
        splitmissingingrs = []
        for ings in row.missingIngrs:
            for ing in nltk.word_tokenize(ings):    #re.findall(r"[\w']+", ings):   #ings.split():
                splitmissingingrs.append(ing)
        splitmissingingrs = [porter.stem(i) for i in splitmissingingrs] ##
        stemmedtitle = [porter.stem(i) for i in nltk.word_tokenize(row.title.lower())]
        
        if any(i in stemmedtitle for i in splitmissingingrs):
            recipeFrame.ix[index,'pctMissing'] = 100
        
    print 'Finished marking recipes where key ingredient is missing...'
    
    closestFrame = recipeFrame[recipeFrame['pctMissing'] <= 20]
    closestFrame = closestFrame[closestFrame['numMissing'] <= 2]
    
    closestFrame = closestFrame.sort_index(by=['numMissing','pctMissing'], ascending=[True,True])
    closestFrame = closestFrame[:10]
    
    print 'Finished slicing and sorting to form closestFrame. Now printing it...'
    
    if closestFrame.empty:
        print 'Sorry, you are not close to any recipe.' 
    else:
        print closestFrame[['title','chef','missingIngrs']]
        
    if chefname:
        graphtitle = 'Most Common Ingredients in Recipes by '+chefname
        graphfilename = 'topingredients-'+chefname+'.jpg'
    else:
        graphtitle = 'Most Common Ingredients in Food Network Recipes'
        graphfilename = 'topingredients.jpg'
        barhFromList(recipeFrame.chef, top=20, title='Biggest Recipe Authors on foodnetwork.com', freqrelto=len(recipeFrame), xlabel='% of all recipes', saveas='topauthors.jpg')
    
    barhFromList(hugeingslist, xlabel='% of recipes using this ingredient', title=graphtitle, saveas=graphfilename, top=40, freqrelto=len(recipeFrame))
    
    print 'Done.'
    
if __name__=="__main__":            
    main()      