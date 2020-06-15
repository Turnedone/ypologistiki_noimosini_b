import pandas as pd
from random import seed
from random import randint
from random import uniform
import numpy as np
from operator import attrgetter


userList = []



class User: # Κλάση που κωδικοποιεί τους χρήστες

     # Εδώ αποθηκεύονται τα άτομα του πληθυσμού για το κάθε χρήστη
    populationSize = 20
    matePropability = 0.6
    mutationChance = 0.4

    def __init__(self, userId):
        self.userId = userId # id χρήστη
        self.bitRatings = [] # bit array χρήστη για τις αξιολογήσεις
        self.ratings = [] # Αξιολογήσεις του χρήστη
        self.ranking = [] # List για τους κοντινότερους γείτονες του χρήστη
        self.populationList = []

    def populate(self): # Δημιουργία πληθυσμού για τον συγκεκριμένο χρήστη
        for num in range(self.populationSize): # μέσω της μεταβλητής populationSize
            randomRatings = np.nan_to_num(self.ratings) # Αντικατάσταση NaN τιμών με 0
            for r in range(len(randomRatings)):
                if randomRatings[r] == 0:
                    randomRatings[r] = randint(1, 5) # Αντικατάσταση τιμών 0 με τυχαία ακέραια τιμή στο [1,5]
            ind = Individual(num, randomRatings, self)
            ind.calculateScore()
            self.populationList.append(ind) # Δημιουργία ατόμου


    def calculateNeighbours(self, rank): # Έρευση των Κ(rank) πιο κοντινών γειτόνων του χρήστη
        pearsonList = []
        idList = []

        for u in userList: # Για κάθε αλλο χρήστη
                uFilled = np.nan_to_num(u.ratings) # Αντικατάσταση NaN τιμών με 0
                sFilled = np.nan_to_num(self.ratings) # Αντικατάσταση NaN τιμών με 0
                pearson = np.corrcoef(sFilled, uFilled)[0, 1] # Υπολογισμός της συσχέτισης Pearson
                pearsonList.append(pearson)
                idList.append(u.userId)
        self.ranking =[x for _,x in sorted(zip(pearsonList, idList), reverse=True)]
        self.ranking = self.ranking[1:rank+1] # Τελική λίστα των Κ(rank) πιο κοντινών γειτόνων του χρήστη

    def selectionRanking(self):
        rankingScores = [] # Λίστα που κρατάει τη κατάταξη
        roulette = [] # Λίστα που παρομοιάζει την ρουλέτα
        oldPopulation = self.populationList # Λίστα που κρατάει την τελευταία μορφή του πληθυσμού
        self.populationList = [] # Διαγραφή των ατόμων για τη δημιουργία νέας γενιάς
        oldPopulation.sort(key=lambda z: z.score, reverse=True) # Ταξινόμιση του πληθυσμού βάση του score τους

        currScore = len(oldPopulation)
        for o in oldPopulation: # For loop για τη δημιουργία της κατάταξης
            rankingScores.append(currScore)
            currScore = currScore - 1

        for index in range(len(rankingScores)): # Μετατροπή της κατάταξης σε πιθανότητες για τη ρουλέτα
            if not roulette:
                roulette.append(rankingScores[index]/sum(rankingScores))
            else:
                roulette.append(rankingScores[index]/sum(rankingScores) + roulette[index-1])

        for index in range(len(rankingScores)):
            spin = uniform(0, 1) # Δημιουργία spin για τη ρουλέτα
            for index1, s in enumerate(roulette):
                if s >= spin:
                    self.populationList.append(oldPopulation[index1]) # Selection του ατόμου βάση του spin
                    break
        self.updateScores()

    def mate(self):
        for index in range(0, len(self.populationList), 2): # For loop για τη διαστάυρωση του πληθυσμού ανά δύο
            p = uniform(0, 1)
            if p <= self.matePropability: # Πιθανότητα διασταύρωσης
                for index1 in range(0, len(self.populationList[index].indRatings)):
                    if self.bitRatings[index] == 1: # For loop για το κάθε μεταβλητό γονίδιο
                        parentChoice = randint(0, 1)
                        if parentChoice == 1: # 50% πιθανότητα το πρώτο παιδί να πάρει γονίδιο απ'τον δεύτερο γονέα
                            self.populationList[index].indRatings[index1] = self.populationList[index+1].indRatings[index1]
                        parentChoice = randint(0, 1)
                        if parentChoice == 1: # 50% πιθανότητα το δευτερο παιδί να πάρει γονίδιο απ'τον πρώτο γονέα
                            self.populationList[index+1].indRatings[index1] = self.populationList[index].indRatings[index1]
        self.updateScores()


    def mutate(self):

        for ind in self.populationList: # Για κάθε άτομο του πληθυσμού
            for index in range(len(ind.indRatings)): # Για κάθε γονίδιο
                if self.bitRatings[index] == 1: # Αν το γονίδιο είναι μεταβλητό
                    p = uniform(0, 1)
                    if p <= self.mutationChance: # Βάση της πιθανότητας μετάλλαξης
                        ind.indRatings[index] = randint(1, 5) # Το γονίδιο μεταλλάσεται με μια τυχαία τιμή

        self.updateScores()

    def updateScores(self):
        for ind in self.populationList:
            ind.calculateScore()








class Individual:


    def __init__(self, indId, indRatings, parentUser):
        self.indId = indId # id του κάθε συγκεκριμένου ατόμου ενός πληθυσμού
        self.indRatings = indRatings # Τα ratings-solution του κάθε ατόμου
        self.parentUser = parentUser # Ο χρήστης από τον οποίο προκύπτει το άτομο
        self.score = 0

    def calculateScore(self):
        self.score = 0
        for u in self.parentUser.ranking: # Μέσω των id's των γειτόνων του parent user του ατόμου
            for usr in userList:
                if usr.userId == u: # Υπολογίζεται ο συντελεστής Pearson
                    userRatings = np.nan_to_num(usr.ratings)
                    pearsonScaled = (np.corrcoef(userRatings, self.indRatings)[0, 1] + 1)/2 # με κανονικοποίηση στο [0,1]
                    self.score = self.score + pearsonScaled # Το score είναι το άθροισμα των επιμέρους συντελεστών Pearson


class Generation:

    def __init__(self, genId, genUser, genPopulation):
        self.genId = genId # Ιd της κάθε γενιάς
        self.genUser = genUser # Ο χρήστης στον οποίο ανήκει η κάθε γενιά
        self.genPopulation = genPopulation # Ο πληθυσμός των ατόμων της κάθε γενιάς
        self.bestSolution = [] # Η βέλτιστη λύση της γενιάς


    def findBest(self): # Μέθοδος για την εύρεση της βέλτιστης λύσης
        best = max(self.genPopulation, key=attrgetter('score'))
        self.bestSolution.append(best)



df = pd.read_csv('u.data', sep='\t', names=['user_id', 'item_id', 'rating', 'timestamp']) # Διαβάζεται το αρχείο και αποθηκεύται σε μορφή pandas
df2 = df.copy() # Δημιουργία αντίγραφου του dataframe
df2 = df2.pivot(index='user_id', columns='item_id', values=['rating']) # Τροποποίηση του πίνακα ώστε να υπάρχει αντιστιχία user_id-item_id με τιμές το rating


for i, x in enumerate(df2.values): # Εμφωλευμένη for για τη διαχείριση της κάθε αξιολόγισης
    userList.append(User(i+1))
    for y in df2.values[i]: #Δημιουργία των πινάκων αξιολόγησης του κάθε χρήστη
        if np.isnan(y):
            userList[i].bitRatings.append(0)
            userList[i].ratings.append(0)
        else:
            userList[i].bitRatings.append(1)
            userList[i].ratings.append(int(y))


def conditionImprove(genList, gen, n):
    if len(genList) <= 50:
        return True
    for index, g in enumerate(genList):
        if g == gen:
            if (genList[index].bestSolution.score - genList[index - n].bestSolution.score)/genList[index - n].bestSolution.score <= 0.01:
                return False
            else:
                return True

def conditionNumberOfGenerations(currGen, limit):
    if currGen <= limit:
        return True
    else:
        return False




generationsList = []
currentGeneration = 0

currentUser = userList[1]
currentUser.calculateNeighbours(10)
currentUser.populate()

generationsList.append(Generation(currentGeneration, currentUser, currentUser.populationList))
generationsList[0].findBest()


currentGeneration = currentGeneration + 1

while conditionNumberOfGenerations(currentGeneration - 1, 100):

    currentUser.mutate()

    currentUser.mate()

    currentUser.selectionRanking()

    generationsList.append(Generation(currentGeneration, currentUser, currentUser.populationList))
    generationsList[currentGeneration].findBest()

    currentGeneration = currentGeneration + 1

for i,x in enumerate(generationsList):
    for y in x.genPopulation:
        print(y.indId)
    print(x.bestSolution[0].score,"\t",i )



