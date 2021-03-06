#! /usr/bin/env python

import json
from getters.single import SingleQuery
from getters.multi import MultiQuery
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class XnaPyCurl(object):
	"""
	XnaPyCurl: Connect and access resources on XNAT
	
	Class requires an input url to the XNAT API from which
	resources are to be pulled
	:param basepage: XNAT API URL
	"""
	def __init__(self,basepage):
		self.basepage = basepage
		self.ci = PKCS1_OAEP.new(RSA.generate(2048))

	def login(self,*creds):
		"""
		login method
		
		gets a session cookie for future actions
		:param creds: user credentials as input as username,password pair
		:return: number of connections
		"""
		self.cxn = SingleQuery(self.basepage)
		ccount = self.cxn.login(*creds)
		self.crds = map(self.ci.encrypt,creds)
		return ccount
	def logout(self):
		"""
		logout method
		
		uses the method from SingleQuery class
		"""
		done = self.cxn.logout()
		return done

	def loadmulti(self,template,subsess,tail):
		"""
		load a multiquery pool
		
		creates a MultiQuery object from instance
		:param template: uri to format for multiquery
		:param subsess: subject-session dict, keys are subjects; values are sessions
		:param tail: columns to output from query
		:return: a list of pulled results
		"""
		mq = MultiQuery(self.basepage)
		ccount = mq.login(*map(self.ci.decrypt,self.crds))
		urilist = [template.format(subj=k,exp=v)+tail for k,v in subsess.iteritems() if v]
		mq = mq(urilist)
		raw = mq.getfromuri()
		mq.logout()
		return raw

	def getsubjects(self,project,uri_tail):
		"""
		get subject data
		
		:param project: name of XNAT project to query
		:param uri_tail: query string to append to the rest call
		:return: a list of dictionaries containing query outcome
		"""
		uri = 'projects/{proj}/subjects?{tail}'.format(proj=project,tail=uri_tail)
		raw = self.cxn.getfromuri(uri)
		return [json.loads(raw)]

	def getexperiments(self,project,uri_tail):
		"""
		get experiment data
		
		:param project: name of XNAT project to query
		:param uri_tail: query string to append to the rest call
		:return: a list of dictionaries containing query outcome
		"""

		uri = 'projects/{proj}/experiments?{tail}'.format(proj=project,tail=uri_tail)
		raw = self.cxn.getfromuri(uri)
		return [json.loads(raw)]

	def getassessors(self,project,subjexpdict,uri_tail):
		"""
		getassessors - get assessor data
		
		:param project: name of XNAT project to query
		:param subjexpdict: dictionary whose keys are subject labels and values
			are the experiments for that subject
		:param uri_tail: query string to append each the rest call
		:return: a list of dictionaries containing query outcome
		"""

		uri = 'projects/{proj}'.format(proj=project)
		uri += '/subjects/{subj}/experiments/{exp}/assessors?'

		raw = self.loadmulti(uri,subjexpdict,uri_tail)
		return map(json.loads,raw)
	def getscans(self,project,subjexpdict,uri_tail):
		"""
		getscans - get scan data
		
		:param project: name of XNAT project to query
		:param subjexpdict: dictionary whose keys are subject labels and values
			are the experiments for that subject
		:param uri_tail: query string to append each the rest call
		:return: a list of dictionaries containing query outcome
		"""

		uri = 'projects/{proj}'.format(proj=project)
		uri += '/subjects/{subj}/experiments/{exp}/scans?'
		raw = self.loadmulti(uri,subjexpdict,uri_tail)
		return map(json.loads,raw)





















