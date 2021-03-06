'''
Created on Oct 27, 2015

@author: Tommi Unruh
'''

from joern.all import JoernSteps
import time
from configurator import Configurator
from results.code_clone_data import CodeCloneData

class ManualCCSearch(object):
    '''
    classdocs
    '''
    UNTRUSTED_DATA = """attacker_sources = [
                "_GET", "_POST", "_COOKIE",
                "_REQUEST", "_ENV", "HTTP_ENV_VARS"
                ]\n"""
    
    SQL_QUERY_FUNCS = """sql_query_funcs = [
                "mysql_query", "pg_query", "sqlite_query"
                ]\n"""
    
    # Gremlin operations
    ORDER_LN = ".order{it.a.lineno <=> it.b.lineno}" # Order by linenumber
    
    def __init__(self, port):
        '''
        Constructor
        '''
        self.j = JoernSteps()
        self.j.setGraphDbURL('http://localhost:%d/db/data/' % (int(port)))
#         self.j.addStepsDir(
#                         Configurator.getPath(Configurator.KEY_PYTHON_JOERN) + 
#                         "/joern/phpjoernsteps"
#                         )
        
        self.j.addStepsDir(
                        Configurator.getPath(Configurator.KEY_BASE_DIR) +
                        "/custom_gremlin_steps"
                           )
        self.j.connectToDatabase()
        
#         self.QUERIES_DIR = Configurator.getPath(Configurator.BASE_DIR) + \
#                         "/gremlin_queries" 
        
    def searchCCOne(self):
        """
        Search for the first vulnerable tutorial (SQL injection from stackoverflow):
        $user_alcohol_permitted_selection = $_POST['alcohol_check']; //Value sent using jquery .load()
        $user_social_club_name_input = $_POST['name']; //Value sent using jquery .load()

        $query="SELECT * FROM social_clubs 
        WHERE name = $user_social_club_name_input";    

        if ($user_alcohol_permitted_selection != "???")
        {
             $query.= "AND WHERE alcohol_permitted = $user_alcohol_permitted_selection";
        }
        """
        # construct gremlin query step by step:
        # 1. Find variable name X of "variable = $_POST[..]"
        # 2. Go to next statement list.
        # (3. Find variable name Y of "variable = $_POST[..]"
        # (4. Go to next statement list.
        # 5. Find variable name Z and string str1 of "variable = string"
        # 6. Check if str1 contains regexp "WHERE any_word=$Y".
        # (7. Go to next statement list.)
        # (8. Check for if-statement with variable $X.)
        # 9. Check if variable $Z is extended using string with regexp
        # "and where any_word=$X"
        # (10. Check for mysql_query($Z))
        
        # all nodes
#         query  = "g.V(NODE_TYPE, TYPE_STMT_LIST).out"
#         
#         # AST_ASSIGN nodes' right side
#         query += ".rval"

        query = "g.V"

        return query
    
    def sqlNewIndirect(self):
        query = self.UNTRUSTED_DATA + self.SQL_QUERY_FUNCS
        
        query += open(self.QUERIES_DIR + "sql_new_indirect.query", 'r').read()
    
        return query
    
    def runQuery(self, query):
        return query
    
    def runTimedQuery(self, myFunction, query=None):
        start = time.time()
        res = None
        try:
            if query:
                res = self.j.runGremlinQuery(myFunction(query))
            else:
                res = self.j.runGremlinQuery(myFunction())

        except Exception as err:
            print "Caught exception:", type(err), err
        
        elapsed = time.time() - start
        
#         print "Query done in %f seconds." % (elapsed)
        result = []
        try:
            for node in res:
                print node
                data = CodeCloneData()
                data.stripDataFromOutput(node)
                data.setQueryTime(elapsed)
                result.append(data)

        except TypeError:
            # res is not iterable, because it is one/no node.
#             print res
            if res:
                data = CodeCloneData()
                data.stripDataFromOutput(node)
                data.setQueryTime(elapsed)
                result.append(data)
                print res
        
        return (result, elapsed)