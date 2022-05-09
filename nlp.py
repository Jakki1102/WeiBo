from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.nlp.v20190408 import nlp_client, models
import json

def get_sentiment(string):
   try:
      cred = credential.Credential("AKIDilfUAfrgBUbWFmRHJ9nFbqtkFcnnOCcq", "97ua4UzNsUxFLJ5g6KQL8kOsDRTIvzuh") 
      httpProfile = HttpProfile()
      httpProfile.endpoint = "nlp.tencentcloudapi.com"

      clientProfile = ClientProfile()
      clientProfile.httpProfile = httpProfile
      client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile) 

      req = models.SentimentAnalysisRequest()
      params = '{"Text":"'+string+'"}'
      req.from_json_string(params)
      
      resp = client.SentimentAnalysis(req)
      positive=json.loads(str(resp.to_json_string()))['Positive']
      result=int(positive*200-100)
      return result

   except TencentCloudSDKException as err:
      print(err) 
      return 0




