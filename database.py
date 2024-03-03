# Sucess !
import mysql.connector
# host='localhost'
# database='test_medical_db'
# user='root



class MySql:
	def __init__(self,host,database,user):
		self.host=host
		self.database=database
		self.user=user
		self.password=None
		
	#for insertions
	def table(self,query,data):
		try:
			
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)

			cursor.execute(query,data)
			connection.commit()

			print("Success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")
	
	def insertData(self,query):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			cursor.execute(query)
			connection.commit()
			print("Success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")
	
	# For parameter Binding and foreing keys
	#use comma after created tuple when binding arguments if it has One Argument 
	def fetchOneForeing(self,query,data):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			cursor.execute(query,data)
			result=cursor.fetchone()
			if result:
				return(result[0])
			else:
				return "No value"
			print("getting success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")

	#For multiple foreing keys data bind
	#executing admin login and super admin login and user login
	def fetchAllMulForeing(self,query,data):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			
			cursor.execute(query,data)
			result=cursor.fetchall()
			return(result)
			print("getting success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")



		

	# FOR SINGLE QUERY
	def fetchOne(self,query):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			
			cursor.execute(query)
			result=cursor.fetchone()
			return result[0]
			print("getting success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")
	
	#FOR SINGLE QUERY WITHOUT BINDING 
	def fetchMultiVal(self,query):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			
			cursor.execute(query)
			result=cursor.fetchall()
			return result
			print("getting success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")
		
	#without binding
	def delete(self, query):

		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			
			cursor.execute(query)
			connection.commit()  # Commit the deletion operation
			print("Deletion successful!")
		except mysql.connector.Error as error:
			print("Query failed: {}".format(error))
		finally:
			if connection is not None and connection.is_connected():
				cursor.close()  # Close the cursor
				connection.close()  # Close the connection
				print("Connection closed!")

	
	

	def deleteMulti(self, query, data):
		connection = None
		try:
			connection = mysql.connector.connect(
				host=self.host,
				database=self.database,
				user=self.user,
				password=None
			)
			cursor = connection.cursor(prepared=True)
			cursor.execute(query, data)
			connection.commit()  # Commit the changes to the database
			print("Deletion successful!")
		except mysql.connector.Error as error:
			print("Query failed: {}".format(error))
		finally:
			if connection is not None and connection.is_connected():
				cursor.close()  # Close the cursor
				connection.close()  # Close the connection
				print("Connection closed!")

		
	#edit..
	def getCount(self,department):

		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			
			query="SELECT count(*) FROM subjects AS s INNER JOIN medical_infor AS mi ON s.subject_id=mi.subject_id INNER JOIN departments AS dep ON s.department_id=dep.id WHERE dep.calling_name=%s AND mi.is_confirm=0 AND mi.is_authenticate=0 ;"
			cursor.execute(query,(department,))
			result=cursor.fetchone()
			return result[0]
			print("getting success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")


	def getMain(self,department):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			
			query="SELECT st.user_id,st.email,first_name,id_card,mi.medical_sheet FROM students AS st INNER JOIN medical_infor AS mi ON st.user_id =mi.user_id INNER JOIN departments AS dep ON st.department_id=dep.id WHERE dep.calling_name=%s AND mi.is_confirm=0 AND mi.is_authenticate=0 ORDER BY mi.recorded_time DESC;"
			cursor.execute(query,(department,))
			result=cursor.fetchall()
			return result
			print("getting success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")
		


	def getUniqeCountYear(self,department):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			
			query="SELECT DISTINCT s.year FROM subjects AS s INNER JOIN departments AS dep ON s.department_id=dep.id WHERE dep.calling_name=%s;"
			cursor.execute(query,(department,))
			result=cursor.fetchall()
			return result
			print("getting success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")

	def getUniqeCountSem(self,department):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			
			query="SELECT DISTINCT s.semester FROM subjects AS s INNER JOIN departments AS dep ON s.department_id=dep.id WHERE dep.calling_name=%s;"
			cursor.execute(query,(department,))
			result=cursor.fetchall()
			return result
			print("getting success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")
	
	def getUniqeCountSub(self,department):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			
			query="SELECT sub.subject_name FROM subjects AS sub INNER JOIN exams AS ex ON ex.subject_id=sub.subject_id INNER JOIN departments AS dep ON dep.id=sub.department_id WHERE dep.calling_name=%s;"
			cursor.execute(query,(department,))
			result=cursor.fetchall()
			return result
			print("getting success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")
	
	#time table data
	def getValues(self,data):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			
			query="SELECT sub.subject_name,subject_code,ex.held_date,start_time,end_time,location FROM departments AS dep INNER JOIN subjects AS sub ON dep.id=sub.department_id INNER JOIN exams AS ex ON sub.subject_id=ex.subject_id WHERE dep.calling_name=%s;"
			cursor.execute(query,data)
			result=cursor.fetchall()
			return(result)
			print("getting success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")

	def getMainSuper(self,dep):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			
			query="SELECT st.user_id,sub.subject_name ,att.attempt, mi.exam_date,mi.exam_location FROM medical_infor AS mi INNER JOIN subjects AS sub ON sub.subject_id=mi.subject_id INNER JOIN attempts AS att ON att.id=mi.attempt_id  INNER JOIN students AS st ON st.user_id=mi.user_id INNER JOIN departments AS dep ON dep.id=sub.department_id  WHERE dep.calling_name=%s AND mi.is_confirm=1 AND mi.is_authenticate=0;"
			cursor.execute(query,(dep,))
			result=cursor.fetchall()
			return result
			print("getting success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")
	

	def update(self, query, data):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			
			cursor.execute(query, data)
			connection.commit()
			print("Success!")
		except mysql.connector.Error as error:
			print("Query failed: {}".format(error))
		finally:
			if connection is not None and connection.is_connected():
				connection.close()
				print("Connection closed!")
	
	def getDynamicRow(self,query,data):
		try:
			connection=mysql.connector.connect(host=self.host,database=self.database,user=self.user,password=self.password)
			cursor=connection.cursor(prepared=True)
			cursor.execute(query,data)
			result=self.cursor.fetchone()
			return(result[0])
			print("getting success !")
		except mysql.connector.Error as error:
			print("query failed {}".format(error))
		finally:
			if connection != None and connection.is_connected():
				connection.close()
				print("Connection Closed !")




# newSql=MySql()
# query="INSERT INTO user VALUES(2,'nimal','nimalPass');"
# newSql.table(query,host,database,user,password)
