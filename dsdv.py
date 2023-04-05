import random
import math
from PIL import Image, ImageDraw, ImageFont

"""
This code runs a simulation of DSDV algorithm. It not only add nodes but also removes nodes from the network
and further simulates nodes rejoining the network. The final output shows routing tables of different nodes
as well as an image of network topology.

__author__ = Jatin Kumar

"""


INFINITY = 10000000

class Row:
  """
  Represents a dsdv table row
  """
  def __init__(self, dest, hop, distance, seqNo):
    self.dest = dest
    self.hop = hop
    self.distance = distance
    self.seqNumber = seqNo

  def toStr(self):
    return "Dest=" + str(self.dest) + ", hop=" + str(self.hop) + ", distance=" + str(self.distance) + ", seqno=" + str(self.seqNumber);


class Node:
  """
  Represents a node in the Mobile Network.
  """
  def __init__(self, name, x,y):
    self.name = name
    self.x = x
    self.y = y
    self.neighbours = set()
    self.table = {}
    self.needToSend = False


  def receive(self, tableFrom, frm, seq):
    """
    Processes DSDV table update message
    :param tableFrom: table of the sender
    :param frm: name of sender
    :param seq: sequence number
    :return:
    """
    found = False
    for destnameFrom in tableFrom.keys():
      if destnameFrom == self.name:
        continue;
      m = tableFrom[destnameFrom]

      if not destnameFrom in self.table.keys():
        self.table[destnameFrom] = Row(m.dest, frm, min(m.distance + 1, INFINITY), m.seqNumber)
        self.needToSend = True
      else:
        t = self.table[destnameFrom]
        if ((m.seqNumber > t.seqNumber and m.distance == INFINITY) or
                (m.dest == t.dest and (m.distance + 1) < t.distance and m.seqNumber >= t.seqNumber)):
          t.distance = min(m.distance + 1, INFINITY)
          t.seqNumber = m.seqNumber
          t.hop = frm
          self.needToSend = True
      u = self.table[destnameFrom]
      if u.distance == INFINITY:
        for r in self.table.values():
          if r.hop== destnameFrom:
            r.distance = INFINITY
            r.seqNumber = seq

    # put sender in the table at distance 1
    if frm in self.table.keys():
        del self.table[frm]
        self.table[frm] =  Row(frm, self.name, 1, seq)

  def toStr(self):
    """
    Returns string representation of a node.
    :return:
    """
    ret = "Node: " + self.name + "\n"
    ret += "Table: " + str(len(self.table.values())) + " entries: \n"
    for r in self.table.values():
      ret += r.toStr() + "\n"
    ret += "\n";
    return ret


class Dsdv:
  """
  Class representing main DSDV algorithm simulation logic
  """
  def __init__(self):
    self.nodes = []
    self.wid = 100
    self.hei = 100
    self.neighbourDist = 20
    self.removedNodes = []
    self.nextSeq = 1

  def Simulate(self):
    """
    Main simulation method
    :return:
    """

    #create nodes
    a = Node("A", self.wid / 2, self.hei / 2)
    self.nodes.append(a)
    for i in range(1, 8):
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
          if  not m.name in n.table.keys():
            n.table[m.name] = Row(m.name, n.name, 1, self.nextSeq)
          if not n.name in m.table.keys():
            m.table[n.name] = Row(n.name, m.name, 1, self.nextSeq)
          m.needToSend = True
          n.needToSend = True

    #Run simulation iterations
    iter = 8000
    self.nextSeq +=1
    remain = len(self.nodes)
    removeNode = None

    lastTime = -1;
    for k in range(iter):
      removeNode = None
      if random.randint(0,999) < 1 and k < (iter-1000):
        nodeInd = random.randint(0,len(self.nodes)-1)
        removeNode = self.nodes[nodeInd]
        trial = 0;
        while len(removeNode.neighbours) > 1 and trial < 10000:
          nodeInd = (nodeInd + 1) % len(self.nodes)
          removeNode = self.nodes[nodeInd]
          trial +=1

        if trial < 10000:
          for ndstr in removeNode.neighbours:
            nd = self.getNode(ndstr, self.nodes)
            if removeNode.name in nd.table.keys():
              nd.table[removeNode.name].distance = INFINITY
              nd.table[removeNode.name].seqNumber = self.nextSeq

            if nd.name in removeNode.table.keys():
              removeNode.table[nd.name].distance = INFINITY
              removeNode.table[nd.name].seqNumber = self.nextSeq

            nd.needToSend = True
            nd.neighbours.remove(removeNode.name)

          self.nextSeq+=1

          for rr in removeNode.table.values():
            rr.distance = INFINITY
          removeNode.table.clear()
          removeNode.neighbours.clear()
          removeNode.needToSend = True
          self.removedNodes.append(removeNode)

        if len(self.removedNodes) > 0:
          if True:
            pending = False
          for nd in self.nodes:
            if nd.needToSend:
              pending = True
          if not pending:
            self.addDeletedNode(self.removedNodes[0])
            self.removedNodes.remove(0)

        for n in self.nodes:
          if not n.needToSend and random.randint(0,99) < 70:
            continue

          for receiverName in n.neighbours:
            receiveNode = self.getNode(receiverName, self.nodes)
            receiveNode.receive(n.table, n.name, self.nextSeq)
            self.nextSeq+=1

          n.needToSend = False
    return self.nodes

  def getRow(self, rows, dest):
    for row in rows.values:
      if row.dest.equals(dest):
        return row
    return None

  def getNode(self, id, nodes):
    for node in nodes:
      if node.name== id:
        return node
    return None

  def isNearby(self, x1, y1, x2, y2):
    if abs(x1 - x2) < self.neighbourDist and abs(y1 - y2) < self.neighbourDist:
      return True
    else:
      return False

  def addDeletedNode(self, nd):
    nd.neighbours.Clear()
    nd.needToSend = False

    x = 20
    y = 34

    nei = self.getNeighbours(x, y)

    while len(nei) == 0:
      x = random.randint(0, self.wid-1)
      y = random.randint(0, self.hei -1)
    nei = self.getNeighbours(x, y)

    neistrs = set()

    for nn in nei:
      if not nn.name.equals(nd.name):
        neistrs.add(nn.name)
    nd.neighbours = neistrs
    nd.x = x
    nd.y = y

    for nnstr in nd.neighbours:
      nn = self.getNode(nnstr, self.nodes)
      nn.neighbours.Add(nd.name)
      nd.neighbours.Add(nn.name)
      if nn.table.containskey(nd.name):
        nn.table.remove(nd.name)
      nn.table.add(nd.name, Row(nd.name, nn.name, 1, self.nextSeq))

      if nd.table.containskey(nn.name):
        nd.table.remove(nn.name)
        nd.table.add(nn.name, Row(nn.name, nd.name, 1, self.nextSeq))

      nd.needToSend = True
      nn.needToSend = True

    self.nextSeq +=1

  def addANode(self, name):
    x = random.randint(0, self.wid-1)
    y = random.randint(0, self.hei-1)
    nei = self.getNeighbours(x, y)
    while len(nei) == 0:
      x = random.randint(0, self.wid -1)
      y = random.randint(0, self.hei-1)
      nei = self.getNeighbours(x, y)
    self.nodes.append(Node(name, x, y))

  def getNeighbours(self, x, y):
    ret = []
    for n in self.nodes:
      if self.isNearby(x, y, n.x, n.y):
        ret.append(n)
    return ret


d = Dsdv();
nodes = d.Simulate()
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
    img1.line(shape, fill="#ff0000", width=0)

img.show()

for n in nodes:
  print(n.toStr())
  print()

print("")




