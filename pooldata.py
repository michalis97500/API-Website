import requests
import typing
import json
import os
from borb.pdf.document import Document  
from borb.pdf.pdf import PDF  
from borb.toolkit.text.simple_text_extraction import SimpleTextExtraction 

def flexpool():
  uri = 'https://api.flexpool.io/v2'
  url = "{}/miner/balance/".format(uri)
  payload = {
    "coin": "ETH",
    "address" : "0xc1caeaa1d3e30eb759076e2d3cc365ff724a5335"
  }
  headers = {}
  response = requests.request("GET", url, headers=headers, params=payload)
  split1 = str(response.text).split("{\"error\":null,\"result\":{\"balance\":")
  split2 = split1[1].split(",")
  return (float(split2[0])/1000000000000000000)

def hiveon():
  dirname = os.path.dirname(__file__)
  filename = os.path.join(dirname, 'PDF/hive.pdf')
  response = requests.post('https://api.pdfshift.io/v3/convert/pdf',
  auth=('api', '0922af7a743449b28ff0573e0ed5f217'),
  json={'source': 'https://hiveon.net/eth?miner=0xc1caeaa1d3e30eb759076e2d3cc365ff724a5335', "sandbox": True},
  stream=True)
  with open(filename, 'wb') as output:
    for chunk in response.iter_content(chunk_size=1024):
      output.write(chunk)
  output.close()
  doc: typing.Optional[Document] = None  
  l: SimpleTextExtraction = SimpleTextExtraction()  
  with open(filename, "rb") as in_file_handle:  
    doc = PDF.loads(in_file_handle, [l])  
  assert doc is not None 
  text = l.get_text_for_page(0)
  split1 = text.split("Expected earnings")
  split2 = split1[2].split("ETH")
  split3 = split2[0].split("USD")
  return(split3[1].strip())

