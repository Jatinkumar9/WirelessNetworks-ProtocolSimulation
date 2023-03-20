import random
import math
from PIL import Image, ImageDraw, ImageFont

"""
This program is a demo for AODV algorithm. It creates upto 15 random nodes. 
Then a source and destination nodes are selected randomly. Finally AODV routing 
algorithm is run from source to destination to find the route. Final route
is displayed in the form of image as well as route and routing tables are printed
in console ouptut. 
"""


INFINITY = 10000000

class Row:
  """
  Represents a Aodv table row
  """
  def __init__(self, dest, hop):
    self.dest = dest
    self.hop = hop

  def toStr(self):
    return "Dest=" + str(self.dest) + ", hop=" + str(self.hop) ;

class Rreq:
  """
  Represents a Aodv Rreq request object
  """
  def __init__(self, reqid, frm, to):
    self.broadcast_id = reqid
    self.source_addr = frm
    self.dest_addr = to

class Rresp:
  """
  Represents a Aodv Rresp response object
  """
  def __init__(self, reqid, frm, to):
    self.broadcast_id = reqid
    self.source_addr = frm
    self.dest_addr = to

class NextToProcess:
  """
  Represents information which a node needs to broadcast in case of Rreq
  or send back in case of Rresp
  """
  def __init__(self, frm, req, resp):
    self.frm = frm
    self.req = req
    self.resp = resp



class Node:
  """
  Represents a node in the Mobile Network.
  """
  def __init__(self, name, x,y):
    self.name = name  #name or unique identifier to the node
    self.x = x        # x location of the node in our map
    self.y = y        # y location of the node in our map
    self.neighbours = set()   # a set containing names/idz of its neighboours
    self.table = {}     # a table containing source to destination hop information
    self.reqs = {}      # a hashtable containing all the requests which this node has seen
    self.nextToProcess= []    # a list contaning request or response which this node needs to forward

  def process(self,aodv):
    """
    This method forwards req or resp object to desired location.
    """
    parr = []
    for p in self.nextToProcess:
      parr.append(p)
    for p in parr:
      if p.req != None:
        self.handleRreq(p.req, p.frm, aodv)
      else:
        self.handleRResp(p.frm, p.resp, aodv)
    self.nextToProcess.clear();

  def handleRreq(self, rreq, frm, aodv):
    """
    Processes a req object by sending it to all neighbours if applicable.
    :param rreq: table of the sender
    :param frm: name of sender
    :param aodv: reference to aodv class to get node from identifier
    :return:
    """
    # already handled request, do nothing
    if rreq.broadcast_id in self.reqs.keys():
      return

    # send response if destination found
    if rreq.dest_addr in self.table.keys() or self.name == rreq.dest_addr:
      fnode = aodv.getNode(frm, aodv.nodes)
      fnode.nextToProcess.append(NextToProcess(self.name, None, Rresp(rreq.broadcast_id, rreq.source_addr, rreq.dest_addr)));
    else:
    # forward request object to all neighbours
      self.reqs[rreq.broadcast_id] = frm
      for nid in self.neighbours:
        nd = aodv.getNode(nid, aodv.nodes)
        nd.nextToProcess.append(NextToProcess(self.name, rreq, None))



  def handleRResp(self, frm, rresp, aodv):
    """
    Handles response packet forwarding. Send the resp to node which corresponding request
    came from.
    :param frm:
    :param rresp:
    :param aodv:
    :return:
    """
    if rresp.source_addr == self.name and  not rresp.dest_addr in self.table.keys():
      self.table[rresp.dest_addr] = frm
      return

    if rresp.dest_addr in self.table.keys():
      return;

    self.table[rresp.dest_addr] = frm

    destback = self.reqs[rresp.broadcast_id]
    destbackNode = aodv.getNode(destback, aodv.nodes)
    destbackNode.handleRResp(self.name, rresp, aodv)
    destbackNode.nextToProcess.append(NextToProcess(self.name, None, rresp))

  def toStr(self):
    """
    Returns string representation of a node.
    :return:
    """
    ret = "Node: " + self.name + "\n"
    ret += "Table: " + str(len(self.table.values())) + " entries: \n"
    for r in self.table.keys():
      ret += "Dest: " + r + ", Hop: " +  self.table[r] + "\n"
    ret += "\n";
    return ret


class Aodv:
  """
  Class representing main Aodv algorithm simulation logic
  """
  def __init__(self):
    self.nodes = []
    self.wid = 100
    self.hei = 100
    self.neighbourDist = 20
    self.removedNodes = []
    self.nextSeq = 1

  def initializeTopology(self, size):
    """
    Main simulation method
    :return:
    """

    #create nodes
    a = Node("A", self.wid / 2, self.hei / 2)
    self.nodes.append(a)
    for i in range(1, size):
      self.addANode(  str(chr(ord('A') + i)))

    #create links between neighbours
    for i in range(0, len(self.nodes)):
      n = self.nodes[i]
      for j in range(0, len(self.nodes)):
        if i == j:
          continue;
        m: object = self.nodes[j]
        if self.isNearby(n.x, n.y, self.nodes[j].x, self.nodes[j].y):
          n.neighbours.add(m.name)
          m.neighbours.add(n.name)
    return self.nodes

  def processRequest(self, frm,  to):
    """
    runs AODV from frm node to to node.
    """
    rreq = Rreq(self.nextSeq, frm, to)
    self.nextSeq+=1
    src = self.getNode(rreq.source_addr, self.nodes)
    src.nextToProcess.append(NextToProcess(src.name, rreq, None))

    cnt = 1
    while cnt > 0:
      cnt = 0
      for nd in self.nodes:
        cnt += len(nd.nextToProcess)
        nd.process(self)
    return self.nodes


  """
  def getRow(self, rows, dest):
    for row in rows.values:
      if row.dest.equals(dest):
        return row
    return None
  """

  def getNode(self, id, nodes):
    for node in nodes:
      if node.name== id:
        return node
    return None

  def isNearby(self, x1, y1, x2, y2):
    """
    Checks if two locations are near by.
    """
    if abs(x1 - x2) < self.neighbourDist and abs(y1 - y2) < self.neighbourDist:
      return True
    else:
      return False

  def addANode(self, name):
    """
    Add a node with given name to topology
    """
    x = random.randint(0, self.wid-1)
    y = random.randint(0, self.hei-1)
    nei = self.getNeighbours(x, y)
    while len(nei) == 0:
      x = random.randint(0, self.wid -1)
      y = random.randint(0, self.hei-1)
      nei = self.getNeighbours(x, y)
    self.nodes.append(Node(name, x, y))

  def getNeighbours(self, x, y):
    """
    returns are list of neighbours which are near this node.
    """
    ret = []
    for n in self.nodes:
      if self.isNearby(x, y, n.x, n.y):
        ret.append(n)
    return ret



d = Aodv()
size = random.randint(5, 15)
nodes = d.initializeTopology(size)

frm =  str(chr(ord('A') + random.randint(0,size-1)))
to =  str(chr(ord('A') + random.randint(0,size-1)))
while frm == to:
  frm = str(chr(ord('A') + random.randint(0, size - 1)))
  to = str(chr(ord('A') + random.randint(0, size - 1)))
nodes = d.processRequest(frm, to)

print("Displaying route from '" + frm + "' to '" + to + "':")


edges = set()
st = d.getNode(frm, nodes)
cnt = 1
while  to in st.table.keys():
  next =  st.table[to]
  edges.add(st.name + "-" + next)
  print(str(cnt) + ": " + st.name + " --> " + next)
  st = d.getNode(next, nodes)
  cnt+=1

w, h = 1000,1000
shape = [(10, 10), (w - 10, h - 10)]

img = Image.new("RGB", (w, h))

img1 = ImageDraw.Draw(img)
img1.rectangle(shape, fill="#ffffff")
r=10

font = ImageFont.load_default()

for n in nodes:
  xx = n.x*r
  yy = n.y *r
  shape = [(xx-5, yy-5), (xx+5, yy+5)]
  img1.ellipse(shape,  fill="#ffff33", outline="red")
  img1.text((xx+10, yy+10), str(n.name), fill="#ff0000", font=font, align="left")

for n in nodes:
  for s in n.neighbours:
    m = d.getNode(s, nodes)
    shape = [n.x * r, n.y * r, m.x * r, m.y * r]
    check1 = n.name + "-" + s
    check2 = s + "-" + n.name
    if check1 in edges or check2 in edges:
      img1.line(shape, fill="#00ff00", width=0)
    else:
      img1.line(shape, fill="#ff0000", width=0)

img.show()

print()
print("Now printing table showing hops:")
for n in nodes:
  print(n.toStr(), end = '')

print("")




