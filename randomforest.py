import statistics
import random
from random import sample
import csv
import sys
import math

# Basic implementation of BST-like structure is inspired by and at points flat out modified from https://www.geeksforgeeks.org/binary-search-tree-set-1-search-and-insertion/

class split():
    def __init__(self, subset, comparison, feature, threshold, identifier):
        self.right=None
        self.left=None
        self.parent=None
        self.data=subset # subset of data stored in node
        self.comparison=comparison # is it checking if data is more or less than threshold
        self.feature=feature # what feature is it using to split
        self.threshold=threshold # what is the threshold
        self.identifier=identifier

class decision_tree():
    def gini_impurity(self, exo, non):
        exo_positive, non_positive = 0,0
        for i in exo: # FINDS LABELS OF EVERYTHING IN PILE
            if i[0] == 1:
                exo_positive+=1
        for i in non:
            if i[0] == 1:
                non_positive+=1
        p1, p2 = exo_positive/(len(exo)+len(non)), non_positive/(len(exo)+len(non))
        impurity = (p1*(1-p1)) + (p2*(1-p2))
        return impurity
    def create_split(self, data, comparison, sample, prev_switched, switch_loop):
        feature = random.choice(sample) # choose feature for a split
        featurelist = [] # lower data down to just the feature-specific data
        for e in data:
            featurelist.append(e[feature])
        threshold = statistics.mean(featurelist) # initial threshold for split
        prev_total = 2 # initialize previous total variable so improvement calculations work
        improvement = 0
        loops = 0
        direction=1
        while improvement >= 0:
            if loops != 0:
                threshold=prev-10 if direction == -1 else prev+10
            exo, non=[], []
            for e in data: # SORTS DATA BY THRESHOLD
                if comparison == ">":
                    exo.append(e) if e[feature] > threshold else non.append(e)
                if comparison == "<":
                    exo.append(e) if e[feature] < threshold else non.append(e)
            total=self.gini_impurity(exo, non)
            improvement = prev_total-total
            if int(sys.argv[4])==1:
                print ("Improvement this round is %s" % improvement)
            log=[[2, 2]]
            if improvement==0 and prev_improvement==0 and loops > 5 and prev_switched != True:
                direction = -direction
                log[0]=[total, threshold]
                print ("Switching directions!")
                prev_switched=True
                switch_loop=loops
            if improvement==0 and prev_improvement==0 and loops > 5 and loops-switch_loop > 3: # STOP IT FROM GETTING STUCK AT 0 IMPROVEMENT
                if total > log[0][0]:
                    threshold=log[0][1]
                print ("Giving up...")
                break
            prev = threshold
            prev_total = total
            prev_improvement = improvement
            loops=loops+1
        return [exo, non, comparison, feature, threshold]
    def create_tree(self, depth, current, data, root, loops, sample):
        comparisons=['<','>']
        global exited
        exited=False
        for e in current[0:2]:
            if root.parent != None and exited==True:
                root=root.parent
            root.comparison=current[2]
            root.feature=current[3]
            root.threshold=current[4]
            if depth != -1:
                if loops >= depth:
                    exited=True
                    break
            if len(current[0])<1 or len(current[1])<1:
                exited=True
                break
            if e==current[0]:
                root.left=split(current[0], None, None, None, "Exo")
                parent=root
                root=root.left
                root.parent=parent
            else:
                root.right=split(current[1], None, None, None, "Non")
                parent=root
                root=root.right
                root.parent=parent
            half = self.create_split(e, comparisons[random.randint(0,1)], sample, False, 0)
            data.append(half)
            self.create_tree(depth, half, data, root, loops+1, sample)
        exited=True
    def inorder(self,root):
        if root:
            self.inorder(root.left)
            print(len(root.data))
            self.inorder(root.right)
    def __init__(self, depth_limit, data, sample):
        comparisons=['<', '>']
        current = self.create_split(data, comparisons[random.randint(0,1)], sample, False, 0)
        self.root = split(data, current[2], current[3], current[4], "Root")
        self.create_tree(depth_limit, current, [], self.root, 1, sample)
        print("Decision tree created!")
    def get_root(self):
        return self.root



def random_forest(trees, depth, data):
    forest=[]
    features=[1,2,3,4]
    for e in range(trees):
        sampled_data=random.choices(data, k=len(data))
        subset=sample(features, math.ceil(math.sqrt(len(features))))
        forest.append(decision_tree(depth, sampled_data, subset))
    consensus=[]
    for i in data:
        votes=[]
        for tree in forest:
            root=tree.get_root()
            while True:
                if root.left==None and root.right==None:
                    if root.identifier=="Non":
                        vote=0
                    else:
                        vote=1
                    votes.append(vote)
                    break
                feature=root.feature
                comparison=root.comparison
                threshold=root.threshold
                if comparison == ">":
                    root=root.left if i[feature] > threshold else root.right
                else:
                    root=root.left if i[feature] < threshold else root.right
        counter=0
        for e in votes:
            if e == 1:
                counter+=1
        if counter == len(votes)/2:
            majority = random.randint(0,1)
        else:
            majority = statistics.mode(votes)
        consensus.append(majority)
    return consensus

def forest_accuracy(consensus, data):
    labels=[]
    for i in data:
          labels.append(i[0])
    correct=0
    for e, n in enumerate(labels):
         if consensus[e]==n:
            correct+=1
    return correct/(len(labels))

with open(sys.argv[1], 'rt') as f:
    reader = csv.reader(f)
    data = list(reader)
    for a in data:
        for b, c in enumerate(a):
            a[b] = float(a[b])
print (forest_accuracy(random_forest(int(sys.argv[2]), int(sys.argv[3]), data), data))

