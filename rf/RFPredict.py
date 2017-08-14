# -*- coding: UTF-8 -*-
#参考http://blog.csdn.net/flying_sfeng/article/details/64133822
import re
def pretty_output(file_path, output_file_path):
	"""将原始debug_string添加缩进，方便人眼看
	"""
	with open(file_path, 'r') as f, open(output_file_path, 'w') as f2:
		for line in f:
			space_count = len(line) - len(line.lstrip())
			new_line = '\t' * (space_count-2) + line.lstrip()
			f2.writelines(new_line)

def getidvalue(rule):
    left_bracket = rule.find('(') + 1
    right_bracket = rule.find(')')
    bracket_content = rule[left_bracket: right_bracket]
    targets=re.findall(r'\-*\d+(?:\.\d+)?',rule)
    if len(targets)==2:
        return int(targets[0]),int(float(targets[1]))

def getTreeSide(rules,target,side):
    try:
        targeti=target+1
        if side=='right':
            tab_count = rules[target].count('\t')
            for i,rule in enumerate(rules):
                if i<=target+1:
                    continue
                tab_count2 = rule.count('\t')
                if tab_count2==tab_count:    
                    targeti=i+1         #Else的下一行
                    break
        rule=rules[targeti]
        rule_content=rule.lstrip()
        if rule_content.startswith('Predict'):
            return rule_content
        index, value = getidvalue(rule)
        return {'index':index,'value':value,'left':getTreeSide(rules,targeti,'left'),'right':getTreeSide(rules,targeti,'right')}
    except:
        print(len(rules))
        print(targeti)
        print('error')

def getTreeFromRules(rules):
    index,value=getidvalue(rules[0])
    root={'index':index,'value':value,'left':getTreeSide(rules,0,'left'),'right':getTreeSide(rules,0,'right')}
    return root


def predict(tree, row):
    if int(row[tree['index']-1]) <= tree['value']:
        if isinstance(tree['left'], dict):
            return predict(tree['left'], row)
        else:
            return tree['left']
    else:
        if isinstance(tree['right'], dict):
            return predict(tree['right'], row)
        else:
            return tree['right']


def bagging_predict(trees,row):
    predictions = [predict(tree, row) for tree in trees]
    return max(set(predictions), key=predictions.count)


def lognow():
    time = __import__('time')
    now = time.strftime('%Y-%m-%d %X', time.localtime())
    print now

class RFPredict():
    def __init__(self, modelPath):
        self.modelPath=modelPath
        self.trees=[]
        self.loadModel()

    def loadModel(self):
        modelPath2='backup_'+self.modelPath
        pretty_output(self.modelPath, modelPath2)

        with open(modelPath2,'r') as file:
            line = file.readline()
            line = file.readline()     #第二行开始
            rules=[]
            while line:
                if line.startswith('Tree'):
                    if len(rules)>0:
                        tree=getTreeFromRules(rules)
                        self.trees.append(tree)
                    rules = []
                else:
                    rules.append(line)
                line=file.readline()
            if len(rules) > 0:         #最后一颗树
                tree = getTreeFromRules(rules)
                self.trees.append(tree)
        print 'model len:'+str(len(self.trees))



    def predict(self,testPath):
        with open(testPath,'r') as file:
            line=file.readline()
            while line:
                vectors=line.split('\t')
                print bagging_predict(self.trees,vectors).replace('\t','').replace('\r','').replace('\n','')
                line=file.readline()


if __name__ == '__main__':
    lognow()
    rfPredict=RFPredict('rf.txt')
    lognow()
    rfPredict.predict('test.txt')
    lognow()


